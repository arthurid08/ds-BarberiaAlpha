from flask import Flask
from database import db
from routes import agendamentos_bp
from models import Cliente, Barbeiro, Servico

app = Flask(__name__)
app.secret_key = "barbearia_alpha_secret_key"

# Configuracao do banco SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializacao das extensoes e rotas
db.init_app(app)
app.register_blueprint(agendamentos_bp)


def seed_dados_iniciais():
    """Cria alguns clientes, barbeiros e serviços na primeira execução,
    apenas para que os selects do formulário não fiquem vazios."""
    if not Cliente.query.first():
        db.session.add_all([
            Cliente(nome="João Pereira", telefone="(11) 90000-0001", email="joao@email.com"),
            Cliente(nome="Marcos Souza", telefone="(11) 90000-0002", email="marcos@email.com"),
        ])
    if not Barbeiro.query.first():
        db.session.add_all([
            Barbeiro(nome="Carlos Silva", especialidade="Corte", disponibilidade="Seg-Sex 9-18"),
            Barbeiro(nome="Mateus Santos", especialidade="Barba", disponibilidade="Ter-Sáb 10-17"),
        ])
    if not Servico.query.first():
        db.session.add_all([
            Servico(nome_do_servico="Corte de Cabelo", descricao="Corte tradicional", preco=50.00),
            Servico(nome_do_servico="Barba Completa", descricao="Barba com toalha quente", preco=40.00),
            Servico(nome_do_servico="Combo Corte + Barba", descricao="Corte e barba", preco=80.00),
        ])
    db.session.commit()


# Criacao automatica das tabelas no primeiro start
with app.app_context():
    db.create_all()
    seed_dados_iniciais()

if __name__ == '__main__':
    app.run(debug=True)
