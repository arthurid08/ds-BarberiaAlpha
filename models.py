from database import db


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)


class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'

    id_barbeiro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=True)
    disponibilidade = db.Column(db.String(100), nullable=True)

    agendamentos = db.relationship('Agendamento', backref='barbeiro', lazy=True)


class Servico(db.Model):
    __tablename__ = 'servicos'

    id_do_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_do_servico = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Numeric(10, 2), nullable=False)

    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'

    id_do_agendamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)
    id_barbeiro = db.Column(db.Integer, db.ForeignKey('barbeiros.id_barbeiro'), nullable=False)
    id_do_servico = db.Column(db.Integer, db.ForeignKey('servicos.id_do_servico'), nullable=False)
    data_hora = db.Column(db.String(50), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    status_pagamento = db.Column(db.String(50), default='Pendente', nullable=False)