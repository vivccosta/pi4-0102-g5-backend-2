"""
Testes unitários para o motor de Blockchain e Criptografia do Timbro.
Execução:
    .venv/bin/python tests/test_blockchain.py
"""

import hashlib
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from blockchain import Blockchain, formatar_hash_0x, normalizar_hash


def test_bloco_genesis():
    """Testa se a blockchain inicializa com o bloco gênesis correto."""
    bc = Blockchain(caminho_arquivo=None)
    assert len(bc) == 1
    genesis = bc.cadeia[0]
    assert genesis.indice == 0
    assert genesis.hash_anterior == "0"
    assert genesis.hash_certificado == "0"
    assert genesis.dados["tipo"] == "genesis"
    print("✓ Bloco gênesis criado corretamente")


def test_criptografia_pdf_sha256():
    """Valida se a criptografia do binário gera SHA-256 com prefixo 0x."""
    pdf_binario = b"%PDF-1.4 certificado binario teste de integridade"
    hash_resultado = Blockchain.criptografar_pdf(pdf_binario)
    hash_esperado = f"0x{hashlib.sha256(pdf_binario).hexdigest()}"

    assert hash_resultado == hash_esperado
    assert hash_resultado.startswith("0x")
    assert len(hash_resultado) == 66  # 0x + 64 caracteres hex
    print("✓ Criptografia do binário do PDF (SHA-256) validada com sucesso")


def test_gravar_certificado_com_binario_pdf():
    """Testa a gravação de um certificado a partir do binário bruto do PDF."""
    bc = Blockchain(caminho_arquivo=None)
    pdf_binario = b"%PDF-1.4 certificado da aluna Maria Silva Santos"
    dados = {
        "nomeAluno": "Maria Silva Santos",
        "curso": "Engenharia de Software",
        "dataConclusao": "2026-10-12",
        "cargaHoraria": 20,
    }

    resultado = bc.gravar_certificado(dados_certificado=dados, binario_pdf=pdf_binario)

    assert resultado["status"] is True
    assert resultado["bloco"] == 1
    assert resultado["hash"] == Blockchain.criptografar_pdf(pdf_binario)
    assert resultado["hashTransacao"].startswith("0x")
    assert len(bc) == 2
    print("✓ Certificado registrado e bloco encadeado a partir do binário do PDF")


def test_encadeamento_entre_blocos():
    """Testa se cada bloco referencia estritamente o hash do bloco anterior."""
    bc = Blockchain(caminho_arquivo=None)

    for i in range(1, 4):
        pdf = f"%PDF-1.4 certificado {i}".encode("utf-8")
        dados = {"nomeAluno": f"Aluno {i}", "curso": "Sistemas", "cargaHoraria": i * 10}
        bc.gravar_certificado(dados, binario_pdf=pdf)

    assert len(bc) == 4  # Gênesis + 3 blocos

    for i in range(1, len(bc)):
        bloco_atual = bc.cadeia[i]
        bloco_anterior = bc.cadeia[i - 1]
        assert bloco_atual.hash_anterior == bloco_anterior.hash_bloco

    print("✓ Encadeamento criptográfico entre múltiplos blocos validado")


def test_validar_cadeia_integra():
    """Testa se a cadeia é reconhecida como íntegra em condições normais."""
    bc = Blockchain(caminho_arquivo=None)
    bc.gravar_certificado({"nome": "Teste"}, binario_pdf=b"pdf1")
    bc.gravar_certificado({"nome": "Teste 2"}, binario_pdf=b"pdf2")

    assert bc.validar_cadeia() is True
    print("✓ Validação de integridade confirmou cadeia íntegra")


def test_deteccao_adulteracao_dados_bloco():
    """Garante que qualquer alteração indevida nos dados de um bloco quebra a cadeia."""
    bc = Blockchain(caminho_arquivo=None)
    bc.gravar_certificado({"nome": "Original"}, binario_pdf=b"pdf_original")

    assert bc.validar_cadeia() is True

    # Simulação de adulteração externa
    bc.cadeia[1].dados["nome"] = "ADULTERADO"
    assert bc.validar_cadeia() is False
    print("✓ Adulteração de conteúdo detectada pela validação da cadeia")


def test_deteccao_adulteracao_elo_encadeamento():
    """Garante que a quebra de vínculo entre blocos é detectada."""
    bc = Blockchain(caminho_arquivo=None)
    bc.gravar_certificado({"nome": "B1"}, binario_pdf=b"pdf1")
    bc.gravar_certificado({"nome": "B2"}, binario_pdf=b"pdf2")

    # Quebrando o elo anterior
    bc.cadeia[2].hash_anterior = "0x0000000000000000000000000000000000000000000000000000000000000000"
    assert bc.validar_cadeia() is False
    print("✓ Quebra de encadeamento detectada pela validação da cadeia")


def test_consultar_por_hash_confirmacao_e_negacao():
    """Testa consulta por hash com e sem 0x, retornando confirmação ou negação."""
    bc = Blockchain(caminho_arquivo=None)
    pdf = b"%PDF-1.4 teste consulta por hash"
    res = bc.gravar_certificado({"aluno": "Caio"}, binario_pdf=pdf)
    hash_gravado = res["hash"]

    # 1. Confirmação com 0x
    c1 = bc.consultar(hash_certificado=hash_gravado)
    assert c1["existe"] is True
    assert c1["encontrado"] is True
    assert c1["bloco"] == 1
    assert c1["dados"]["aluno"] == "Caio"

    # 2. Confirmação sem 0x
    c2 = bc.consultar(hash_certificado=hash_gravado[2:])
    assert c2["existe"] is True
    assert c2["bloco"] == 1

    # 3. Negação para hash inexistente
    c3 = bc.consultar(hash_certificado="0x" + "f" * 64)
    assert c3["existe"] is False
    assert c3["encontrado"] is False
    assert "não encontrado" in c3["mensagem"]
    print("✓ Consulta por hash (confirmação e negação) validada")


def test_consultar_por_binario_confirmacao_e_negacao():
    """Testa consulta passando o binário direto (criptografa antes)."""
    bc = Blockchain(caminho_arquivo=None)
    pdf_cadastrado = b"%PDF-1.4 certificado cadastrado"
    pdf_nao_cadastrado = b"%PDF-1.4 certificado outro"

    bc.gravar_certificado({"aluno": "Aluno Cadastrado"}, binario_pdf=pdf_cadastrado)

    # 1. Confirmação ao passar o binário cadastrado
    c1 = bc.consultar(binario_pdf=pdf_cadastrado)
    assert c1["existe"] is True
    assert c1["encontrado"] is True
    assert c1["bloco"] == 1
    assert c1["dados"]["aluno"] == "Aluno Cadastrado"

    # 2. Negação ao passar binário não cadastrado
    c2 = bc.consultar(binario_pdf=pdf_nao_cadastrado)
    assert c2["existe"] is False
    assert c2["encontrado"] is False
    assert "não encontrado" in c2["mensagem"]
    print("✓ Consulta por binário de PDF (criptografa antes e consulta) validada")


def test_rejeicao_duplicata():
    """Garante que o mesmo certificado não pode ser inserido duas vezes."""
    bc = Blockchain(caminho_arquivo=None)
    pdf = b"%PDF-1.4 certificado unico duplicata teste"

    r1 = bc.gravar_certificado({"aluno": "A"}, binario_pdf=pdf)
    assert r1["status"] is True

    r2 = bc.gravar_certificado({"aluno": "A de novo"}, binario_pdf=pdf)
    assert r2["status"] is False
    assert "já registrado" in r2["erro"]
    print("✓ Rejeição de certificados duplicados validada")


def test_persistencia_em_disco():
    """Testa se a blockchain persiste dados e recupera perfeitamente do arquivo JSON."""
    pasta_tmp = tempfile.mkdtemp()
    arquivo_db = os.path.join(pasta_tmp, "blockchain.json")

    try:
        # 1. Grava na primeira instância
        bc1 = Blockchain(caminho_arquivo=arquivo_db)
        pdf = b"%PDF-1.4 persistencia teste"
        res = bc1.gravar_certificado({"aluno": "Persistente"}, binario_pdf=pdf)
        hash_cert = res["hash"]

        assert os.path.exists(arquivo_db)

        # 2. Recria nova instância a partir do arquivo persistido (simulando restart do container)
        bc2 = Blockchain(caminho_arquivo=arquivo_db)
        assert len(bc2) == 2
        assert bc2.validar_cadeia() is True

        consulta = bc2.consultar(hash_certificado=hash_cert)
        assert consulta["existe"] is True
        assert consulta["dados"]["aluno"] == "Persistente"
        print("✓ Persistência em disco JSON e recuperação pós-reinício validadas")
    finally:
        shutil.rmtree(pasta_tmp, ignore_errors=True)


if __name__ == "__main__":
    testes = [
        test_bloco_genesis,
        test_criptografia_pdf_sha256,
        test_gravar_certificado_com_binario_pdf,
        test_encadeamento_entre_blocos,
        test_validar_cadeia_integra,
        test_deteccao_adulteracao_dados_bloco,
        test_deteccao_adulteracao_elo_encadeamento,
        test_consultar_por_hash_confirmacao_e_negacao,
        test_consultar_por_binario_confirmacao_e_negacao,
        test_rejeicao_duplicata,
        test_persistencia_em_disco,
    ]

    falhas = 0
    print("\nIniciando execução dos testes unitários da Blockchain...")
    print("-" * 60)
    for t in testes:
        try:
            t()
        except AssertionError as e:
            print(f"✗ Falha em {t.__name__}: {e}")
            falhas += 1
        except Exception as e:
            print(f"✗ Erro inesperado em {t.__name__}: {e}")
            falhas += 1

    print("-" * 60)
    print(f"Resultado: {len(testes) - falhas}/{len(testes)} passaram com sucesso.")
    if falhas > 0:
        sys.exit(1)
