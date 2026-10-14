# CT10: consultarHash

| Linha | Valor |
| :--- | :--- |
| **Fronteira** | WebSocket |
| **Quem chama** | Backend 1 (API) |
| **Quem responde** | Backend 2 (Blockchain) |
| **Atende** | E3 |
| **Como chamar** | Mensagem enviada via WebSocket no evento consultarHash (JSON via WS) |

## Entrada

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hash | texto | sim | 0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069 |

## Saída

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| existe | booleano | sim | true |
| hash | texto | sim | 0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069 |
| timestamp | texto | não | 2026-10-12T20:45:00Z |

## Erros

| Quando | O que volta |
| :--- | :--- |
| Conexão WebSocket com Backend 2 indisponível | Falha de conexão / WebSocket desconectado |
| Hash com formato inválido | Mensagem de erro de parâmetro inválido via WS |