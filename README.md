# Timbro: Backend 2 — Servidor WebSocket de Blockchain & Criptografia

Módulo servidor WebSocket responsável pela centralização da criptografia de certificados e manutenção da cadeia de blocos acadêmica do projeto **Timbro** (PUC-Campinas | Projeto Integrador IV).

---

## 🎯 Papel na Arquitetura

O **Backend 2** atua exclusivamente como o **servidor WebSocket** do sistema de blockchain, aguardando conexões do **Backend 1** (cliente).

### Responsabilidades:
1. **Receber o binário do certificado (PDF)**, criptografar via **SHA-256** (formato canônico `0x...`) e encadear em um novo bloco da blockchain.
2. **Consultar certificados na blockchain:**
   - Recebe um **hash** OU um **binário de PDF** (se binário, calcula o SHA-256 antes).
   - Verifica se o hash existe na cadeia:
     - Se sim: retorna uma **confirmação** (`existe: true`, metadados e bloco).
     - Se não: retorna uma **negação** (`existe: false`).
3. **Imutabilidade e Encadeamento:**
   - Mantém os blocos matematicamente interligados (`hashAnterior == hashBloco_anterior`).
   - Não utiliza mineradores (sem Proof-of-Work desnecessário).
   - A invalidação/revogação de certificados é gerida no banco de dados MongoDB pelo Backend 1, mantendo a blockchain puramente imutável e focada na integridade documental.

---

## 🏗️ Estrutura de Diretórios

```
pi4-0102-g5-backend-2/
├── Dockerfile                   # Imagem Docker com Python e websockets (porta 8000)
├── requirements.txt             # Dependência: websockets>=13.0
├── README.md                    # Documentação do módulo
├── data/                        # Diretório de persistência da blockchain
│   └── blockchain.json          # Estado serializado dos blocos
├── docs/                        # Contratos de WebSocket e ADRs
│   ├── adr/
│   │   ├── 001-isolar-a-blockchain.md
│   │   └── 002-centralizar-a-criptografia-na-blockchain.md
│   └── contratos/
│       ├── CT5-gravarCertificado.md
│       ├── CT6-retornoGravacaoBlockchain.md
│       └── CT10-consultarHash.md
├── src/
│   ├── blockchain.py            # Estrutura do Bloco, Blockchain e Criptografia SHA-256
│   └── servidor.py              # Servidor WebSocket assíncrono (ws://backend2:8000/ws/blockchain)
└── tests/
    ├── test_blockchain.py       # Testes unitários do motor criptográfico
    └── test_servidor.py         # Testes de integração WebSocket (cliente -> servidor)
```

---

## 🔌 Protocolo WebSocket (`ws://backend2:8000/ws/blockchain`)

O Backend 1 conecta no endpoint WebSocket e troca mensagens no formato JSON.

### 1. Gravar Certificado (`gravarCertificado`) — CT5 / CT6

O Backend 1 envia os metadados do aluno e o binário do PDF (em base64):

**Mensagem enviada pelo Backend 1:**
```json
{
  "evento": "gravarCertificado",
  "nomeAluno": "Maria Silva Santos",
  "cpfAluno": "123.456.789-00",
  "curso": "Engenharia de Software",
  "dataConclusao": "2026-10-12",
  "cargaHoraria": 20,
  "arquivoPdf": "<string_base64_do_pdf>"
}
```

**Resposta do Backend 2 (Confirmação):**
```json
{
  "evento": "retornoGravacaoBlockchain",
  "status": true,
  "hash": "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  "hashTransacao": "0x3e1a89c...",
  "bloco": 1,
  "timestamp": "2026-11-07T17:40:00Z"
}
```

---

### 2. Consultar Certificado (`consultarHash`) — CT10 / CT11

O Backend 1 pode consultar enviando o **hash** OU o **binário do PDF** (em base64):

#### Opção A — Consulta por Hash:
```json
{
  "evento": "consultarHash",
  "hash": "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
}
```

#### Opção B — Consulta por Binário do PDF:
```json
{
  "evento": "consultarHash",
  "arquivoPdf": "<string_base64_do_pdf>"
}
```
*(O Backend 2 calcula automaticamente o SHA-256 do binário e pesquisa na cadeia).*

#### Resposta — Confirmação (Certificado Existe):
```json
{
  "evento": "retornoConsultaBlockchain",
  "status": true,
  "existe": true,
  "encontrado": true,
  "hash": "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  "bloco": 1,
  "timestamp": "2026-11-07T17:40:00Z",
  "dados": {
    "nomeAluno": "Maria Silva Santos",
    "cpfAluno": "123.456.789-00",
    "curso": "Engenharia de Software",
    "dataConclusao": "2026-10-12",
    "cargaHoraria": 20
  }
}
```

#### Resposta — Negação (Certificado Não Existe):
```json
{
  "evento": "retornoConsultaBlockchain",
  "status": false,
  "existe": false,
  "encontrado": false,
  "hash": "0x...",
  "mensagem": "Hash não encontrado na blockchain."
}
```

---

### 3. Operações Utilitárias

- **`validarCadeia`**:
  - Envio: `{"evento": "validarCadeia"}`
  - Resposta: `{"evento": "retornoValidarCadeia", "status": true, "integra": true, "totalBlocos": 2}`
- **`listarBlocos`**:
  - Envio: `{"evento": "listarBlocos"}`
  - Resposta: `{"evento": "retornoListarBlocos", "status": true, "total": 2, "blocos": [...]}`

---

## 🚀 Como Executar

### 1. Execução Local

```bash
cd pi4-0102-g5-backend-2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Iniciar o servidor WebSocket
python src/servidor.py
```

### 2. Execução via Docker

```bash
cd pi4-0102-g5-backend-2
docker build -t timbro-backend-2 .
docker run -d --name backend2 -p 8000:8000 timbro-backend-2
```

---

## 🧪 Bateria de Testes

Para executar os testes unitários e de integração WebSocket:

```bash
cd pi4-0102-g5-backend-2
.venv/bin/python tests/test_blockchain.py
.venv/bin/python tests/test_servidor.py
```
