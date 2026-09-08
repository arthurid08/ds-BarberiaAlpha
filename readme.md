 Sistema de Agendamento - Barbearia Navalha & Estilo

## Este repositório contém a aplicação web desenvolvida em Flask para gerenciamento de agendamentos da Barbearia Navalha & Estilo.

## Integrantes do Grupo
* **Arthur Ignacio Delia**
* **Gustavo Campos Ferreira Da Cruz**
* **Pedro Henrique Guedes Lima**
* **Rafael Fernandes Silva**

## Escolha do Padrão Arquitetural & Justificativa

Padrão Escolhido: Monolítico

Justificativa técnica:

Ao nosso ver, o padrão monolítico se adequa de forma mais eficaz à nossa equipe de pequeno porte (4 pessoas), pela estrutura simplificada e de fácil implantação. O modelo monolítico engloba múltiplas funcionalidades em uma única aplicação, facilitando o desenvolvimento, a manutenção, os testes e o gerenciamento do projeto. Além disso, reduz a complexidade de infraestrutura e a necessidade de comunicação entre diferentes serviços, tornando sua implantação mais rápida e adequada ao contexto do sistema.


## Diagrama de Entidade-Relacionamento (DER)
[Diagrama do Banco de Dados](der.png)


## Mapeamento de Evento (Arquitetura Orientada a Eventos)

Nome do Evento: "Quando o agendamento é realizado"

Reações Automatizadas do Sistema:

1. Atualização da agenda e persistência no banco de dados: Registra o novo agendamento no banco de dados (salvando cliente, data, horário e barbeiro) e altera o status do horário para "Ocupado", bloqueando automaticamente novas solicitações no mesmo slot.

2. Disparo de notificação de confirmação: Envia uma mensagem/notificação automática de confirmação (via e-mail ou WhatsApp) para o cliente com os detalhes da reserva e alerta o barbeiro responsável sobre o novo atendimento agendado.


## Requisitos do Sistema

## Requisitos Funcionais (RF)
Os Requisitos Funcionais descrevem as funcionalidades diretas que o sistema oferece aos usuários:

* **RF01 - Autenticação e Controle de Acesso (Login):** O sistema deve permitir o acesso apenas a usuários autenticados via login com usuário e senha, mantendo rotas protegidas e oferecendo a opção de encerramento de sessão (Logout).
* **RF02 - Gestão de Agendamentos (CRUD):** O sistema deve permitir criar, visualizar, pesquisar e excluir agendamentos de serviços da barbearia.
* **RF03 - Alteração de Status do Agendamento:** O sistema deve permitir alternar o status do pagamento/agendamento entre "Pendente" e "Confirmado".
* **RF04 - Gestão de Clientes:** O sistema deve permitir o cadastro e a exclusão de clientes, com vinculação automática de seus agendamentos.
* **RF05 - Seleção Dinâmica de Horários e Impedimento de Conflitos:** O sistema deve disponibilizar horários pré-definidos para agendamento e ocultar/desabilitar automaticamente os horários que já foram agendados para uma determinada data e barbeiro.
* **RF06 - Validação do Lado do Servidor:** O sistema deve validar no back-end se um horário já está ocupado por outro cliente antes de efetivar o agendamento.
* **RF07 - Painel de Métricas e Indicadores:** O sistema deve exibir indicadores no topo do painel informando o total de agendamentos, o quantitativo de confirmados vs. pendentes e o faturamento total bruto.
* **RF08 - Filtro e Busca:** O sistema deve permitir filtrar a lista de agendamentos pesquisando pelo nome do cliente ou pelo nome do serviço.


## Requisitos Não Funcionais (RNF)
Os Requisitos Não Funcionais definem os aspectos de qualidade, segurança, usabilidade e arquitetura do sistema:

* **RNF01 - Usabilidade e Máscara de Entrada:** O campo de telefone no cadastro de clientes deve implementar formatação automática via JavaScript no padrão `(XX) XXXXX-XXXX`, limitando a entrada ao tamanho correto.
* **RNF02 - Interface Responsiva:** A interface do painel web deve se adaptar a diferentes tamanhos de tela (desktop, tablet e dispositivos móveis), garantindo rolagem adequada em tabelas extensas.
* **RNF03 - Segurança de Sessão:** As sessões do usuário devem utilizar chave secreta configurada no servidor e cookies de sessão gerenciados via `Flask-Login`.
* **RNF04 - Desempenho e Atualizações Leves (AJAX):** A consulta de horários ocupados deve ser realizada de forma assíncrona (Fetch/AJAX), sem a necessidade de recarregar a página inteira.
* **RNF05 - Persistência de Dados:** O sistema deve utilizar banco de dados relacional (SQLite via Flask-SQLAlchemy) para garantia de consistência relacional (chaves estrangeiras entre clientes, barbeiros, serviços e agendamentos).
* **RNF06 - Arquitetura Modular:** A aplicação deve ser organizada seguindo o padrão MVC/Blueprints (divisão em `routes.py`, `models.py`, `database.py` e `templates/`), facilitando a manutenção e a escalabilidade do código.



## Arquitetura
* `database.py` — instância central do SQLAlchemy.
* `models.py` — tabelas do ORM (Cliente, Barbeiro, Serviço, Agendamento), baseadas no DER.
* `routes.py` — Blueprint com as rotas e regras de negócio (CRUD + filtro).
* `app.py` — ponto de entrada: configuração e inicialização do servidor.

## Mapeamento e Estratégia de Cache
Tela / Função Otimizada: Consulta do Catálogo de Serviços (/) e Horários Ocupados (/horarios-ocupados).

Tecnologia Utilizada: Redis em memória.

Justificativa Técnica: As listagens de serviços da barbearia (ex: "Corte Masculino", "Barba Completa") possuem baixa frequência de alteração no banco de dados. Ao armazenar esses dados em cache (Redis), reduz-se drasticamente o tempo de resposta da rota pública e evita-se a execução de consultas repetidas ao banco de dados relacional (SQLite) a cada carregamento da página por múltiplos clientes simultâneos.


## Como rodar
pip install flask flask_sqlalchemy
python app.py
pip install flask-login
pip install redis flask-caching celery


O banco `barbearia.db` é criado automaticamente na primeira execução (não é versionado — veja `.gitignore`).

## Mapeamento dos Padrões de Comunicação

Fluxo 1 — Comunicação Síncrona (API REST)

Funcionalidade: Validação de Autenticação do Administrador (/login).  

Tipo de Comunicação: HTTP/REST (Síncrono).  

Descrição do Fluxo: O usuário preenche as credenciais no formulário e envia uma requisição POST para a rota /login.

A aplicação consulta de imediato o banco de dados via SQLAlchemy para verificar o nome de usuário e a senha.  

A requisição permanece em aguardo ativo até o processamento.  

O servidor devolve a resposta HTTP síncrona: autorizando o acesso e redirecionando para a listagem restrita ou emitindo um alerta de erro de autenticação na tela.


Fluxo 2 — Comunicação Assíncrona (Filas / Mensageria)

Funcionalidade: Disparo de Notificação de Confirmação de Agendamento.  

Tipo de Comunicação: Orientada a Eventos / Fila de Mensagens (AMQP / RabbitMQ ou Celery).  

Descrição do Fluxo:O cliente conclui o agendamento no formulário web enviando uma requisição para a rota /criar. 

O backend valida a disponibilidade de horário e persiste o registro no banco de dados de forma imediata.  

Após a gravação, o sistema publica uma mensagem no barramento/fila referente ao evento "Quando o agendamento é realizado" contendo as informações da reserva. 

O cliente recebe a confirmação na interface imediatamente sem aguardar o envio externo. 

Em segundo plano, um worker consome a mensagem da fila e envia as notificações de confirmação (e-mail/WhatsApp) para o cliente e para o barbeiro responsável de maneira desacoplada.


## API Getaway

API Gateway: O API Gateway atuará como ponto único de entrada (Reverse Proxy/Router) interceptando todas as requisições oriundas do Navegador/Web App do cliente. Ele roteia chamadas de busca de horários para rotas públicas e requisições de administração para as rotas autenticadas (/login, /atualizar-status, /deletar) do backend Flask.

Estratégia de Cache: Tela/Função: Consulta do Catálogo de Serviços (rota /) e Verificação de Horários Ocupados (rota /horarios-ocupados).  Tecnologia: Redis em memória.  Justificativa: Os serviços oferecidos (ex: "Corte Masculino", "Barba Completa") e seus preços mudam com raríssima frequência. Além disso, a rota /horarios-ocupados é consultada via requisições AJAX assíncronas no frontend sempre que o usuário seleciona um barbeiro ou data. Armazenar as respostas desses dados em cache evita consultas repetidas ao banco de dados SQLite (barbearia.db), reduz o tempo de resposta da página pública e evita sobrecarga no servidor.


