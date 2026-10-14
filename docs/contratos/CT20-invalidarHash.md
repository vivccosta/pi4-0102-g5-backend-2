# CT20: invalidarHash

| Linha | Valor |
| :--- | :--- |
| **Fronteira** | Externo |
| **Quem chama** | Backend 1 |
| **Quem responde** | Backend 2 (Blockchain) |
| **Atende** | E6 |
| **Como chamar** | Chamada RPC via WebSocket invalidarHash |

## Entrada

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hash | texto | sim | 0x7f83b1657ff1fc... |

## Saída

| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| sucesso | booleano | sim | true |
| hashRevogado | texto | sim | 0x7f83b1657ff1fc... |

## Erros

| Quando | O que volta |
| :--- | :--- |
| O hash não foi encontrado na blockchain | Transaction Revert (Erro na execução do contrato inteligente) |
| Timeout de conexão com o serviço | Exception: Connection Timeout |