### CT3: retornoGravacaoBlockchain

| Linha | Valor |
| :--- | :--- |
| **Fronteira** | Interno |
| **Quem chama** | Backend 2 (Blockchain) |
| **Quem responde** | Backend 1 (API) |
| **Atende** | E2 |
| **Como chamar** | Mensagem recebida via WebSocket no evento retornoGravacaoBlockchain (JSON via WS) |

## Entrada

|Campo         | Tipo  | Obrigatório | Exemplo|
| :--- | :--- | :--- | :--- |
| nomeAluno     | texto | sim         | Maria Silva Santos |
| curso         | texto | sim         | Engenharia de Software |
| dataConclusao | texto | sim         | 2026-10-12 |

#### Saída
| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hashTransacao | texto | sim | 0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069 |
| status | booleano | sim | true |

#### Erros
| Quando | O que volta |
| :--- | :--- |
| Transação rejeitada ou inválida na rede | Mensagem com confirmado: false e motivo do erro |