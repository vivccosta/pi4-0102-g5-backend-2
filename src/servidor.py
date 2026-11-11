"""
Servidor WebSocket para o Backend 2 (Motor de Blockchain & Criptografia - Timbro).
Atua como o servidor WebSocket que recebe conexões do Backend 1 (cliente).

Operações WebSocket atendidas:
1. 'gravarCertificado': recebe o binário do certificado (base64) e metadados,
   criptografa com SHA-256, cria o bloco e encadeia na blockchain.
2. 'consultarHash': recebe um hash OU um binário (se binário, criptografa antes),
   verifica se existe na cadeia de blocos e retorna uma confirmação ou negação.
3. 'validarCadeia': retorna a integridade matemática de toda a cadeia.
4. 'listarBlocos': lista todos os blocos encadeados.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import websockets

from blockchain import Blockchain, formatar_hash_0x, normalizar_hash

# Configuração de armazenamento e porta
STORAGE_PATH = os.environ.get(
    "BLOCKCHAIN_STORAGE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "data", "blockchain.json"),
)
PORTA = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "0.0.0.0")

blockchain = Blockchain(caminho_arquivo=STORAGE_PATH)


def log(msg: str):
    """Log formatado com data e hora no console."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stdout.write(f"[{agora}] [WebSocket] {msg}\n")
    sys.stdout.flush()


def decodificar_binario_pdf(valor: Any) -> Optional[bytes]:
    """Converte valor de entrada (base64 ou bytes) em bytes do binário do PDF."""
    if isinstance(valor, bytes):
        return valor
    if isinstance(valor, str):
        try:
            return base64.b64decode(valor)
        except Exception:
            return None
    return None


def processar_gravar_certificado(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa a solicitação de gravação de certificado:
    Recebe os metadados e o binário, calcula o SHA-256 e encadeia o bloco.
    Devolve o idRequisicao recebido para que o Backend 1 correlacione a Thread HTTP.
    """
    id_requisicao = dados.get("idRequisicao") or dados.get("id")
    campo_binario = dados.get("arquivoPdf") or dados.get("binario") or dados.get("binarioPdf")
    hash_fornecido = dados.get("hash")

    binario_pdf = None
    if campo_binario:
        binario_pdf = decodificar_binario_pdf(campo_binario)
        if not binario_pdf:
            resposta = {
                "evento": "retornoGravacaoBlockchain",
                "status": False,
                "erro": "O campo do binário do PDF (arquivoPdf/binario) não é um base64 válido ou está vazio.",
            }
            if id_requisicao is not None:
                resposta["idRequisicao"] = id_requisicao
            return resposta
    elif not hash_fornecido:
        resposta = {
            "evento": "retornoGravacaoBlockchain",
            "status": False,
            "erro": "É obrigatório fornecer o binário do certificado (arquivoPdf) ou o hash.",
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta

    # Metadados do certificado para o bloco
    metadados_bloco = {
        "nomeAluno": dados.get("nomeAluno", ""),
        "cpfAluno": str(dados.get("cpfAluno") or dados.get("cpf") or dados.get("documentoAluno") or ""),
        "curso": dados.get("curso", ""),
        "dataConclusao": str(dados.get("dataConclusao", "")),
        "cargaHoraria": dados.get("cargaHoraria", 0),
        "registradoEm": datetime.utcnow().isoformat() + "Z",
    }

    # Encadear na blockchain
    resultado = blockchain.gravar_certificado(
        dados_certificado=metadados_bloco,
        binario_pdf=binario_pdf,
        hash_certificado=hash_fornecido,
    )

    if resultado["status"]:
        log(f"Certificado gravado com sucesso no Bloco #{resultado['bloco']} | Hash: {resultado['hash']} | idRequisicao: {id_requisicao}")
        resposta = {
            "evento": "retornoGravacaoBlockchain",
            "status": True,
            "hash": resultado["hash"],
            "hashTransacao": resultado["hashTransacao"],
            "bloco": resultado["bloco"],
            "timestamp": resultado["timestamp"],
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta
    else:
        log(f"Falha ao gravar certificado: {resultado.get('erro')}")
        resposta = {
            "evento": "retornoGravacaoBlockchain",
            "status": False,
            "hash": resultado.get("hash"),
            "erro": resultado.get("erro", "Falha na gravação do bloco."),
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta


def processar_consultar_hash(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa a consulta: recebe um hash OU um binário.
    Se for binário, criptografa com SHA-256 antes e verifica na cadeia de blocos.
    Retorna confirmação (se existe) ou negação (se não existe).
    """
    id_requisicao = dados.get("idRequisicao") or dados.get("id")
    campo_binario = dados.get("arquivoPdf") or dados.get("binario") or dados.get("binarioPdf")
    hash_fornecido = dados.get("hash")

    binario_pdf = None
    if campo_binario:
        binario_pdf = decodificar_binario_pdf(campo_binario)
        if not binario_pdf:
            resposta = {
                "evento": "retornoConsultaBlockchain",
                "status": False,
                "statusConsulta": False,
                "existe": False,
                "encontrado": False,
                "erro": "Binário do PDF inválido para consulta.",
            }
            if id_requisicao is not None:
                resposta["idRequisicao"] = id_requisicao
            return resposta

    if not binario_pdf and not hash_fornecido:
        resposta = {
            "evento": "retornoConsultaBlockchain",
            "status": False,
            "statusConsulta": False,
            "existe": False,
            "encontrado": False,
            "erro": "É necessário fornecer um 'hash' ou o binário do certificado ('arquivoPdf').",
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta

    # Consulta na blockchain
    resultado = blockchain.consultar(hash_certificado=hash_fornecido, binario_pdf=binario_pdf)

    if resultado["existe"]:
        log(f"Consulta de certificado: CONFIRMADO (Bloco #{resultado['bloco']} - {resultado['hash']}) | idRequisicao: {id_requisicao}")
        resposta = {
            "evento": "retornoConsultaBlockchain",
            "status": True,
            "statusConsulta": True,
            "existe": True,
            "encontrado": True,
            "hash": resultado["hash"],
            "bloco": resultado["bloco"],
            "timestamp": resultado["timestamp"],
            "dados": resultado["dados"],
            "hashBloco": resultado["hashBloco"],
            "hashAnterior": resultado["hashAnterior"],
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta
    else:
        log(f"Consulta de certificado: NEGADO (Hash não localizado: {resultado.get('hash')}) | idRequisicao: {id_requisicao}")
        resposta = {
            "evento": "retornoConsultaBlockchain",
            "status": False,
            "statusConsulta": True,
            "existe": False,
            "encontrado": False,
            "hash": resultado.get("hash"),
            "mensagem": "Hash não encontrado na blockchain.",
        }
        if id_requisicao is not None:
            resposta["idRequisicao"] = id_requisicao
        return resposta


def processar_invalidar_hash(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trata pedidos de invalidação caso o Backend 1 envie via WebSocket.
    Responde confirmando para não travar a Thread HTTP no Backend 1.
    """
    id_requisicao = dados.get("idRequisicao") or dados.get("id")
    hash_fornecido = dados.get("hash")
    hash_formatado = formatar_hash_0x(hash_fornecido) if hash_fornecido else ""
    log(f"Invalidação de hash solicitada para {hash_formatado} | idRequisicao: {id_requisicao}")

    resposta = {
        "evento": "retornoInvalidacaoBlockchain",
        "sucesso": True,
        "hashRevogado": hash_formatado,
    }
    if id_requisicao is not None:
        resposta["idRequisicao"] = id_requisicao
    return resposta


def processar_mensagem_json(objeto: Dict[str, Any]) -> Dict[str, Any]:
    """Identifica o evento recebido e despacha para a função correspondente."""
    evento = (
        objeto.get("evento")
        or objeto.get("operacao")
        or objeto.get("acao")
        or objeto.get("tipo")
        or ""
    ).strip()

    # Normalização de nomes de eventos
    evento_lower = evento.lower()

    if evento_lower in ("gravarcertificado", "gravar-certificado", "gravar", "registrarcertificado"):
        return processar_gravar_certificado(objeto)

    elif evento_lower in ("consultarhash", "consultar-hash", "consultarcertificado", "consultar", "validarcertificado"):
        return processar_consultar_hash(objeto)

    elif evento_lower in ("invalidarhash", "invalidar-hash", "revogar", "revogarcertificado"):
        return processar_invalidar_hash(objeto)

    elif evento_lower in ("validarcadeia", "validar-cadeia"):
        integra = blockchain.validar_cadeia()
        return {
            "evento": "retornoValidarCadeia",
            "status": True,
            "integra": integra,
            "totalBlocos": len(blockchain),
        }

    elif evento_lower in ("listarblocos", "listar-blocos", "blocos"):
        return {
            "evento": "retornoListarBlocos",
            "status": True,
            "total": len(blockchain),
            "blocos": blockchain.listar_blocos(),
        }

    elif evento_lower in ("ping",):
        return {"evento": "pong", "status": True, "servico": "backend-2-blockchain"}

    # Inferência automática caso a mensagem venha sem o campo 'evento'
    if "nomeAluno" in objeto and ("arquivoPdf" in objeto or "binario" in objeto):
        return processar_gravar_certificado(objeto)

    if "hash" in objeto or "arquivoPdf" in objeto:
        return processar_consultar_hash(objeto)

    return {
        "status": False,
        "erro": f"Evento não reconhecido: '{evento}'. Eventos aceitos: 'gravarCertificado', 'consultarHash', 'validarCadeia', 'listarBlocos'.",
    }


async def conexao_handler(websocket):
    """Manipula uma conexão WebSocket estabelecida com o cliente (Backend 1)."""
    origem = websocket.remote_address
    log(f"Cliente conectado: {origem}")

    try:
        async for mensagem in websocket:
            # 1. Tratar mensagem em bytes brutos (ex: cliente enviou binário do PDF direto)
            if isinstance(mensagem, bytes):
                log(f"Recebido frame binário puro ({len(mensagem)} bytes). Criptografando e consultando...")
                resultado = blockchain.consultar(binario_pdf=mensagem)
                resposta = {
                    "evento": "retornoConsultaBlockchain",
                    "status": resultado["existe"],
                    "existe": resultado["existe"],
                    "encontrado": resultado["existe"],
                    "hash": resultado.get("hash"),
                    "bloco": resultado.get("bloco"),
                    "dados": resultado.get("dados"),
                }
                await websocket.send(json.dumps(resposta, ensure_ascii=False))
                continue

            # 2. Tratar mensagem em texto (JSON)
            try:
                objeto = json.loads(mensagem)
            except json.JSONDecodeError:
                erro_payload = {
                    "status": False,
                    "erro": "Mensagem recebida não é um JSON válido.",
                }
                await websocket.send(json.dumps(erro_payload))
                continue

            # Processar e enviar resposta
            resposta = processar_mensagem_json(objeto)
            await websocket.send(json.dumps(resposta, ensure_ascii=False))

    except websockets.exceptions.ConnectionClosedOK:
        log(f"Cliente desconectou normalmente: {origem}")
    except websockets.exceptions.ConnectionClosedError as e:
        log(f"Conexão com cliente interrompida: {origem} ({e})")
    except Exception as e:
        log(f"Erro inesperado no handler de conexão: {e}")
    finally:
        log(f"Sessão finalizada com: {origem}")


async def main():
    log("=" * 60)
    log("  TIMBRO - Backend 2: Servidor WebSocket de Blockchain & Criptografia")
    log("=" * 60)
    log(f"  Host: {HOST} | Porta: {PORTA}")
    log(f"  Arquivo de persistência: {STORAGE_PATH}")
    log(f"  Blocos atuais na cadeia: {len(blockchain)}")
    log(f"  Integridade da cadeia: {'OK' if blockchain.validar_cadeia() else 'CORROMPIDA'}")
    log("=" * 60)

    # Inicia o servidor WebSocket atendendo em qualquer rota (/ws/blockchain, /, etc.)
    async with websockets.serve(conexao_handler, HOST, PORTA):
        log(f"Servidor WebSocket pronto e escutando em ws://{HOST}:{PORTA}/ws/blockchain")
        await asyncio.Future()  # Mantém o servidor executando indefinidamente


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Encerrando servidor WebSocket...")
