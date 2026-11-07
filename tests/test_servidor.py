"""
Testes de integração WebSocket para o Backend 2 (Blockchain & Criptografia).
Inicia o servidor WebSocket em porta de teste e conecta um cliente real via websockets.
"""

import asyncio
import base64
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import websockets

import servidor
from blockchain import Blockchain

PORTA_TESTE = 18090
WS_URL = f"ws://127.0.0.1:{PORTA_TESTE}/ws/blockchain"


async def executar_testes_websocket():
    pasta_tmp = tempfile.mkdtemp()
    arquivo_db = os.path.join(pasta_tmp, "blockchain_ws_test.json")

    # Inicializar blockchain limpa de teste
    servidor.blockchain = Blockchain(caminho_arquivo=arquivo_db)

    print("\nExecutando testes de integração WebSocket do Backend 2...")
    print("-" * 60)

    # Iniciar servidor WebSocket
    async with websockets.serve(servidor.conexao_handler, "127.0.0.1", PORTA_TESTE):
        # Conectar cliente WebSocket (simulando o Backend 1)
        async with websockets.connect(WS_URL) as ws:
            print(f"✓ Conexão WebSocket estabelecida em {WS_URL}")

            # ------------------------------------------------------------------ #
            # Teste 1: Gravar certificado com binário do PDF em base64 (CT5/CT6)
            # ------------------------------------------------------------------ #
            pdf_conteudo = b"%PDF-1.4 binario de teste do certificado da aluna Maria"
            pdf_base64 = base64.b64encode(pdf_conteudo).decode("ascii")

            msg_gravar = {
                "evento": "gravarCertificado",
                "nomeAluno": "Maria Silva Santos",
                "curso": "Engenharia de Software",
                "dataConclusao": "2026-10-12",
                "cargaHoraria": 20,
                "arquivoPdf": pdf_base64,
            }
            await ws.send(json.dumps(msg_gravar))
            resp = json.loads(await ws.recv())

            assert resp["evento"] == "retornoGravacaoBlockchain"
            assert resp["status"] is True
            assert resp["bloco"] == 1
            assert resp["hash"].startswith("0x")
            hash_certificado = resp["hash"]
            print(f"✓ Evento 'gravarCertificado' gravou bloco #{resp['bloco']} (Hash: {hash_certificado[:18]}...)")

            # ------------------------------------------------------------------ #
            # Teste 2: Rejeitar gravação de certificado duplicado
            # ------------------------------------------------------------------ #
            await ws.send(json.dumps(msg_gravar))
            resp_dup = json.loads(await ws.recv())

            assert resp_dup["status"] is False
            assert "já registrado" in resp_dup["erro"]
            print("✓ Gravação de duplicata rejeitada com status=false")

            # ------------------------------------------------------------------ #
            # Teste 3: Consultar por HASH -> Confirmação (existe=True)
            # ------------------------------------------------------------------ #
            msg_consulta_hash = {
                "evento": "consultarHash",
                "hash": hash_certificado,
            }
            await ws.send(json.dumps(msg_consulta_hash))
            resp_cons1 = json.loads(await ws.recv())

            assert resp_cons1["evento"] == "retornoConsultaBlockchain"
            assert resp_cons1["status"] is True
            assert resp_cons1["existe"] is True
            assert resp_cons1["encontrado"] is True
            assert resp_cons1["bloco"] == 1
            assert resp_cons1["dados"]["nomeAluno"] == "Maria Silva Santos"
            print("✓ Evento 'consultarHash' por HASH retornou confirmação (existe=True)")

            # ------------------------------------------------------------------ #
            # Teste 4: Consultar por BINÁRIO (criptografa antes) -> Confirmação
            # ------------------------------------------------------------------ #
            msg_consulta_bin = {
                "evento": "consultarHash",
                "arquivoPdf": pdf_base64,
            }
            await ws.send(json.dumps(msg_consulta_bin))
            resp_cons2 = json.loads(await ws.recv())

            assert resp_cons2["status"] is True
            assert resp_cons2["existe"] is True
            assert resp_cons2["encontrado"] is True
            assert resp_cons2["hash"] == hash_certificado
            print("✓ Evento 'consultarHash' por BINÁRIO criptografou e retornou confirmação (existe=True)")

            # ------------------------------------------------------------------ #
            # Teste 5: Consultar HASH inexistente -> Negação (existe=False)
            # ------------------------------------------------------------------ #
            hash_inexistente = "0x" + "0" * 64
            msg_consulta_inex = {
                "evento": "consultarHash",
                "hash": hash_inexistente,
            }
            await ws.send(json.dumps(msg_consulta_inex))
            resp_inex = json.loads(await ws.recv())

            assert resp_inex["status"] is False
            assert resp_inex["existe"] is False
            assert resp_inex["encontrado"] is False
            assert "não encontrado" in resp_inex["mensagem"]
            print("✓ Evento 'consultarHash' com hash inexistente retornou negação (existe=False)")

            # ------------------------------------------------------------------ #
            # Teste 6: Consultar BINÁRIO não cadastrado -> Negação (existe=False)
            # ------------------------------------------------------------------ #
            outro_pdf = base64.b64encode(b"%PDF-1.4 outro documento qualquer").decode("ascii")
            msg_consulta_outro = {
                "evento": "consultarHash",
                "arquivoPdf": outro_pdf,
            }
            await ws.send(json.dumps(msg_consulta_outro))
            resp_outro = json.loads(await ws.recv())

            assert resp_outro["status"] is False
            assert resp_outro["existe"] is False
            assert resp_outro["encontrado"] is False
            print("✓ Evento 'consultarHash' com binário não cadastrado retornou negação (existe=False)")

            # ------------------------------------------------------------------ #
            # Teste 7: Frame binário puro (envio direto de bytes)
            # ------------------------------------------------------------------ #
            await ws.send(pdf_conteudo)  # bytes brutos
            resp_frame_bin = json.loads(await ws.recv())

            assert resp_frame_bin["existe"] is True
            assert resp_frame_bin["hash"] == hash_certificado
            print("✓ Frame binário puro de PDF recebido e consultado com sucesso")

            # ------------------------------------------------------------------ #
            # Teste 8: Validar Cadeia
            # ------------------------------------------------------------------ #
            await ws.send(json.dumps({"evento": "validarCadeia"}))
            resp_val = json.loads(await ws.recv())

            assert resp_val["integra"] is True
            assert resp_val["totalBlocos"] == 2
            print("✓ Evento 'validarCadeia' confirmou integridade estrutural")

            # ------------------------------------------------------------------ #
            # Teste 9: Listar Blocos
            # ------------------------------------------------------------------ #
            await ws.send(json.dumps({"evento": "listarBlocos"}))
            resp_blocos = json.loads(await ws.recv())

            assert resp_blocos["status"] is True
            assert resp_blocos["total"] == 2
            assert len(resp_blocos["blocos"]) == 2
            print("✓ Evento 'listarBlocos' retornou a cadeia de blocos")

    shutil.rmtree(pasta_tmp, ignore_errors=True)
    print("-" * 60)
    print("Todos os testes de integração WebSocket passaram com sucesso! ✓\n")


if __name__ == "__main__":
    asyncio.run(executar_testes_websocket())
