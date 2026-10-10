# ADR 0004: Centralizar a criptografia no container do backend-blockchain
Status: aceito

**Contexto:** O sistema necessita gerar hashes e evidências criptográficas dos certificados para garantir a integridade dos dados, sendo preciso definir onde essa lógica pesada e sensível deve residir.

**Decisão:** Localizar a lógica de criptografia e o tratamento de hashes exclusivamente dentro do container do backend dedicado à blockchain.

**Alternativas consideradas:**

Realizar a criptografia no frontend via navegador: descartado por expor regras sensíveis e depender do poder de processamento do cliente.

Deixar a criptografia no backend de api: descartado para manter a integridade e imutabilidade encapsulada no módulo de blockchain.

**Consequências:**

Positivas: Centralização da segurança e consistência das evidências criptográficas em um único componente isolado.

Negativas: Acoplamento da lógica de hash ao módulo de blockchain, exigindo chamadas extras de comunicação entre os backends.
