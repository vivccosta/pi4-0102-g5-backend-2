# Contrato CT27: consultarBlocoEHash

| Linha | Valor |
| :--- | :--- |
| **Fronteira** | WebSocket |
| **Quem chama** | Backend 1 (API) |
| **Quem responde** | Backend 2 (Blockchain) |
| **Atende** | E7 |
| **Como chamar** | Canal `/blockchain`, mensagem do tipo `consultarBlocoEHash` |

## Entrada
| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| hashPdf | texto | sim | `0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d67728` |

## Saída
| Campo | Tipo | Obrigatório | Exemplo |
| :--- | :--- | :--- | :--- |
| blocoEncontrado | booleano | sim | `true` |
| hashBloco | texto | sim | `0x3a2b1c...` |
| statusBlockchain | um de: ativo, revogado | sim | `ativo` |

## Erros
| Quando | O que volta |
| :--- | :--- |
| Hash não localizado na blockchain | `blocoEncontrado: false` |
| Falha de comunicação com o motor blockchain | Erro `FALHA_CONEXAO_BLOCKCHAIN` |