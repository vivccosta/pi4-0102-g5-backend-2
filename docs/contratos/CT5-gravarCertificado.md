### CT2: gravarCertificado

| Linha | Valor |
| :--- | :--- |
| **Fronteira** | Externo |
| **Quem chama** | Backend 1 (API) |
| **Quem responde** | Backend 2 (Blockchain) |
| **Atende** | E2 |
| **Como chamar** | Mensagem WebSocket no evento gravarCertificado (JSON via WS) |

#### Entrada
| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| nomeAluno | texto | sim | Maria Silva Santos |
| curso | texto | sim | Engenharia de Software |
| dataConclusao | texto | sim | 2026-10-12 |
| cargaHoraria | inteiro | sim | 20 |

#### Saída
| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hash | texto | sim | 0x7f83b1657ff1fc53b92dc18 |
| status | booleano | sim | true |

#### Erros
| Quando | O que volta |
| :--- | :--- |
| Falha de execução na Blockchain | Transaction Revert / Out of Gas |
| Timeout de conexão | Exception: Connection Timeout |