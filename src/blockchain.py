"""
Módulo de Blockchain e Criptografia do Timbro (Backend 2).

Responsabilidades:
- Centralizar o cálculo de hashes criptográficos SHA-256 do binário de certificados em PDF.
- Manter o encadeamento cronológico e imutável dos blocos (cadeia de blocos acadêmica).
- Validar a integridade estrutural de toda a cadeia.
- Permitir consulta de existência por hash ou por binário (calculando a criptografia antes).
- Persistir o estado da cadeia em arquivo JSON.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def normalizar_hash(valor_hash: str) -> str:
    """Remove espaços, converte para minúsculas e remove prefixo 0x se presente."""
    limpo = valor_hash.strip().lower()
    if limpo.startswith("0x"):
        limpo = limpo[2:]
    return limpo


def formatar_hash_0x(valor_hash: str) -> str:
    """Garante que o hash comece com o prefixo canônico 0x."""
    limpo = normalizar_hash(valor_hash)
    return f"0x{limpo}"


def criptografar_binario(binario: bytes) -> str:
    """Calcula o SHA-256 do binário fornecido e retorna no formato canônico 0x..."""
    digest = hashlib.sha256(binario).hexdigest()
    return f"0x{digest}"


class Bloco:
    """
    Representa um bloco individual da blockchain acadêmica do Timbro.

    Campos:
    - indice: posição sequencial do bloco (0 = gênesis)
    - timestamp: data e hora de criação em UTC (ISO 8601)
    - dados: metadados do certificado (nomeAluno, cpfAluno, curso, dataConclusao, cargaHoraria)
    - hashCertificado: SHA-256 do binário do PDF do certificado (com prefixo 0x)
    - hashAnterior: hash do bloco imediatamente anterior
    - hashBloco: SHA-256 de todo o conteúdo do bloco, assegurando o encadeamento
    """

    def __init__(
        self,
        indice: int,
        dados: Dict[str, Any],
        hash_certificado: str,
        hash_anterior: str,
        timestamp: Optional[str] = None,
        hash_bloco: Optional[str] = None,
    ):
        self.indice = indice
        self.dados = dados
        self.hash_certificado = formatar_hash_0x(hash_certificado) if hash_certificado != "0" else "0"
        self.hash_anterior = formatar_hash_0x(hash_anterior) if hash_anterior != "0" else "0"
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.hash_bloco = hash_bloco or self.calcular_hash()

    def calcular_hash(self) -> str:
        """Calcula o hash SHA-256 determinístico de todo o conteúdo do bloco."""
        conteudo = json.dumps(
            {
                "indice": self.indice,
                "timestamp": self.timestamp,
                "dados": self.dados,
                "hashCertificado": self.hash_certificado,
                "hashAnterior": self.hash_anterior,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        digest = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o bloco para representação em dicionário/JSON."""
        return {
            "indice": self.indice,
            "timestamp": self.timestamp,
            "dados": self.dados,
            "hashCertificado": self.hash_certificado,
            "hashAnterior": self.hash_anterior,
            "hashBloco": self.hash_bloco,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bloco":
        """Reconstrói um bloco a partir de um dicionário serializado."""
        return cls(
            indice=data["indice"],
            dados=data["dados"],
            hash_certificado=data["hashCertificado"],
            hash_anterior=data["hashAnterior"],
            timestamp=data["timestamp"],
            hash_bloco=data["hashBloco"],
        )


class Blockchain:
    """
    Cadeia de blocos com encadeamento criptográfico SHA-256 e persistência em arquivo JSON.
    Não utiliza mineradores / Proof-of-Work.
    """

    def __init__(self, caminho_arquivo: Optional[str] = None):
        self.caminho_arquivo = caminho_arquivo
        self.cadeia: List[Bloco] = []
        self._indice_hash: Dict[str, Bloco] = {}

        if self.caminho_arquivo and os.path.exists(self.caminho_arquivo):
            self._carregar_arquivo()
        else:
            self._criar_bloco_genesis()
            self._salvar_arquivo()

    # ------------------------------------------------------------------ #
    #  Persistência simples
    # ------------------------------------------------------------------ #

    def _salvar_arquivo(self) -> None:
        """Salva a cadeia atual em arquivo JSON."""
        if not self.caminho_arquivo:
            return

        diretorio = os.path.dirname(self.caminho_arquivo)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio, exist_ok=True)

        payload = {
            "cadeia": [bloco.to_dict() for bloco in self.cadeia],
        }

        caminho_tmp = f"{self.caminho_arquivo}.tmp"
        with open(caminho_tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(caminho_tmp, self.caminho_arquivo)

    def _carregar_arquivo(self) -> None:
        """Carrega a cadeia a partir do arquivo JSON existente."""
        try:
            with open(self.caminho_arquivo, "r", encoding="utf-8") as f:
                payload = json.load(f)

            self.cadeia = [Bloco.from_dict(item) for item in payload.get("cadeia", [])]
            self._reconstruir_indice()

            if not self.cadeia:
                self._criar_bloco_genesis()
                self._salvar_arquivo()
        except Exception as e:
            print(f"[Blockchain] Erro ao carregar arquivo de persistência: {e}. Criando nova cadeia.")
            self.cadeia = []
            self._criar_bloco_genesis()
            self._salvar_arquivo()

    def _reconstruir_indice(self) -> None:
        """Reconstrói o índice de busca rápida por hash do certificado."""
        self._indice_hash = {}
        for bloco in self.cadeia:
            if bloco.hash_certificado != "0":
                chave_normalizada = normalizar_hash(bloco.hash_certificado)
                self._indice_hash[chave_normalizada] = bloco

    # ------------------------------------------------------------------ #
    #  Inicialização
    # ------------------------------------------------------------------ #

    def _criar_bloco_genesis(self) -> None:
        """Cria o bloco gênesis da blockchain."""
        bloco_genesis = Bloco(
            indice=0,
            dados={"tipo": "genesis", "descricao": "Timbro Blockchain Genesis Block"},
            hash_certificado="0",
            hash_anterior="0",
            timestamp="2026-01-01T00:00:00Z",
        )
        self.cadeia = [bloco_genesis]
        self._reconstruir_indice()

    # ------------------------------------------------------------------ #
    #  Criptografia e Gravação
    # ------------------------------------------------------------------ #

    @staticmethod
    def criptografar_pdf(binario_pdf: bytes) -> str:
        """Gera o hash SHA-256 a partir dos bytes brutos de um certificado PDF."""
        return criptografar_binario(binario_pdf)

    def gravar_certificado(
        self,
        dados_certificado: Dict[str, Any],
        binario_pdf: Optional[bytes] = None,
        hash_certificado: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Recebe o binário do certificado (ou o hash já calculado), criptografa com SHA-256
        e joga na cadeia de blocos com encadeamento estrito ao bloco anterior.

        Retorna confirmação com status, hash do certificado, hash da transação e índice do bloco.
        """
        # 1. Criptografa o binário recebido ou valida o hash informado
        if binario_pdf is not None:
            hash_cert_calculado = self.criptografar_pdf(binario_pdf)
        elif hash_certificado is not None:
            hash_cert_calculado = formatar_hash_0x(hash_certificado)
        else:
            return {
                "status": False,
                "erro": "É necessário fornecer o binário do certificado (arquivoPdf) ou o hash.",
            }

        chave_normalizada = normalizar_hash(hash_cert_calculado)

        # 2. Verificar se o certificado já existe na cadeia
        if chave_normalizada in self._indice_hash:
            return {
                "status": False,
                "hash": hash_cert_calculado,
                "erro": "Certificado já registrado na blockchain.",
            }

        # 3. Encadeia o novo bloco ao último bloco existente
        bloco_anterior = self.cadeia[-1]
        novo_indice = len(self.cadeia)

        novo_bloco = Bloco(
            indice=novo_indice,
            dados=dados_certificado,
            hash_certificado=hash_cert_calculado,
            hash_anterior=bloco_anterior.hash_bloco,
        )

        self.cadeia.append(novo_bloco)
        self._indice_hash[chave_normalizada] = novo_bloco
        self._salvar_arquivo()

        return {
            "status": True,
            "hash": hash_cert_calculado,
            "hashTransacao": novo_bloco.hash_bloco,
            "bloco": novo_bloco.indice,
            "timestamp": novo_bloco.timestamp,
        }

    # ------------------------------------------------------------------ #
    #  Consulta de Certificado (por Hash ou por Binário)
    # ------------------------------------------------------------------ #

    def consultar(
        self,
        hash_certificado: Optional[str] = None,
        binario_pdf: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Recebe um hash OU um binário (se for binário, criptografa antes com SHA-256)
        e verifica se esse hash existe na cadeia:
        - Se sim: retorna uma confirmação (existe: True).
        - Se não: retorna uma negação (existe: False).
        """
        if binario_pdf is not None:
            hash_para_busca = self.criptografar_pdf(binario_pdf)
        elif hash_certificado is not None:
            hash_para_busca = formatar_hash_0x(hash_certificado)
        else:
            return {
                "status": False,
                "existe": False,
                "encontrado": False,
                "erro": "É necessário fornecer um hash ou o binário do certificado para consulta.",
            }

        chave_normalizada = normalizar_hash(hash_para_busca)
        bloco = self._indice_hash.get(chave_normalizada)

        if bloco is None:
            # Retorna negação
            return {
                "status": False,
                "existe": False,
                "encontrado": False,
                "hash": hash_para_busca,
                "mensagem": "Hash não encontrado na blockchain.",
            }

        # Retorna confirmação
        return {
            "status": True,
            "existe": True,
            "encontrado": True,
            "hash": bloco.hash_certificado,
            "bloco": bloco.indice,
            "timestamp": bloco.timestamp,
            "hashBloco": bloco.hash_bloco,
            "hashAnterior": bloco.hash_anterior,
            "dados": bloco.dados,
        }

    # ------------------------------------------------------------------ #
    #  Integridade e Utilidades
    # ------------------------------------------------------------------ #

    def validar_cadeia(self) -> bool:
        """
        Percorre toda a blockchain do bloco gênesis até o topo verificando:
        1. Se o hash de cada bloco corresponde deterministicamente ao seu conteúdo.
        2. Se o elo de encadeamento com o bloco anterior está íntegro.
        """
        for i in range(1, len(self.cadeia)):
            bloco_atual = self.cadeia[i]
            bloco_anterior = self.cadeia[i - 1]

            if bloco_atual.hash_bloco != bloco_atual.calcular_hash():
                return False

            if bloco_atual.hash_anterior != bloco_anterior.hash_bloco:
                return False

        return True

    def listar_blocos(self) -> List[Dict[str, Any]]:
        """Retorna todos os blocos serializados em dicionário."""
        return [bloco.to_dict() for bloco in self.cadeia]

    def __len__(self) -> int:
        return len(self.cadeia)
