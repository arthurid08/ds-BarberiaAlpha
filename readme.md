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
![Diagrama do Banco de Dados](docs/der.png)


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


## Como rodar

```
pip install flask flask_sqlalchemy
python app.py
pip install flask-login

O banco `barbearia.db` é criado automaticamente na primeira execução (não é versionado — veja `.gitignore`).



