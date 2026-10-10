# ADR 0001: Isolar a blockchain em um container Docker separado
Status: aceito

**Contexto:** A arquitetura do projeto exige a divisão dos serviços em múltiplos containers Docker, sendo necessário separar as responsabilidades de regra de negócio central da camada de registro distribuído.

**Decisão:** Executar o serviço de blockchain em um container Docker dedicado e isolado dos demais componentes da aplicação.

**Alternativas consideradas:**

Rodar a lógica da blockchain no mesmo container do backend principal: descartado por violar a arquitetura distribuída exigida e acoplar excessivamente os serviços.

Utilizar um serviço de blockchain externo em nuvem: descartado por ser limitado ou não gratuito.

**Consequências:**

Positivas: Modularidade clara, facilidade de escalabilidade independente e atendimento estrito às regras da arquitetura distribuída.

Negativas: Maior complexidade na configuração da rede interna e comunicação via rede entre os containers.
