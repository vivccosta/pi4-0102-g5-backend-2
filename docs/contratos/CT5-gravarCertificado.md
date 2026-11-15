# CT5: gravarCertificado

| Linha | Valor |
| :--- | :--- |
| Fronteira | WebSocket |
| Quem chama | Backend 1 |
| Quem responde | Backend 2 |
| Atende | E2 |
| Como chamar | Mensagem WebSocket no evento gravarCertificado (JSON via WS) |

Entrada

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| emissorId | inteiro | sim | 102 |
| nomeAluno | texto | sim | Maria Silva Santos |
| cpfAluno | Inteiro | sim | 123.456.789-10 |
| curso | texto | sim | Engenharia de Software |
| cargaHoraria | inteiro | sim | 120 |
| dataConclusao | texto | sim | 2026-06-30 |
| status | texto | sim | valido |
| dataEmissao | texto | sim | 2026-06-30 |

Saída:

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hash | texto | sim | 0x7f83b1657ff1fc53b92dc18 |
| status | booleano | sim | true |

Erros:

| Quando | O que volta |
| :--- | :--- |
| Falha de execução na Blockchain | Transaction Revert / Out of Gas |
| Timeout de conexão | Exception: Connection Timeout |
