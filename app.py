from flask import Flask
from database import db
from models import Usuario, Cliente, Barbeiro, Servico, Agendamento
from routes import agendamentos_bp
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configurações da aplicação
app.config['SECRET_KEY'] = 'chave_secreta_barbearia'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do Banco de Dados
db.init_app(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'agendamentos.login'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registro das rotas
app.register_blueprint(agendamentos_bp)

# Criação das tabelas e dados iniciais
with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(email='admin@barbearia.com').first():
        db.session.add(Usuario(
            username='admin',
            email='admin@barbearia.com',
            telefone='(11) 99999-9999',
            senha=generate_password_hash('123'),
            tipo_acesso='admin'
        ))

    if not Barbeiro.query.first():
        barbeiros_iniciais = [
            Barbeiro(nome='Carlos Santos', especialidade='Corte e Barba'),
            Barbeiro(nome='Lucas Lima', especialidade='Degradê e Pigmentação')
        ]
        db.session.add_all(barbeiros_iniciais)

    if not Servico.query.first():
        servicos_iniciais = [
            Servico(nome_do_servico='Corte Masculino', preco=35.00),
            Servico(nome_do_servico='Barba Completa', preco=25.00),
            Servico(nome_do_servico='Cabelo + Barba', preco=55.00)
        ]
        db.session.add_all(servicos_iniciais)

    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)