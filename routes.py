from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Agendamento, Cliente, Barbeiro, Servico

agendamentos_bp = Blueprint('agendamentos', __name__)


# aba de buscar cliente
@agendamentos_bp.route('/', methods=['GET'])
def listar():
    termo_busca = request.args.get('busca', '').strip()

    consulta = Agendamento.query.join(Cliente).join(Servico)

    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Cliente.nome.ilike(f'%{termo_busca}%'),
                Servico.nome_do_servico.ilike(f'%{termo_busca}%')
            )
        )

    agendamentos = consulta.order_by(Agendamento.id_do_agendamento.desc()).all()

    todos = Agendamento.query.all()
    total_agendamentos = len(todos)
    confirmados = sum(1 for a in todos if a.status_pagamento == 'Confirmado')
    pendentes = sum(1 for a in todos if a.status_pagamento == 'Pendente')
    faturamento_total = float(sum(a.valor_total for a in todos if a.status_pagamento == 'Confirmado'))

    return render_template(
        'INDEX.html',
        agendamentos=agendamentos,
        clientes=Cliente.query.order_by(Cliente.nome).all(),
        barbeiros=Barbeiro.query.order_by(Barbeiro.nome).all(),
        servicos=Servico.query.order_by(Servico.nome_do_servico).all(),
        total_agendamentos=total_agendamentos,
        confirmados=confirmados,
        pendentes=pendentes,
        faturamento_total=faturamento_total,
        busca=termo_busca
    )


# Incluir cliente q ja foi cadastrado (ta no final do codigo)
@agendamentos_bp.route('/criar', methods=['POST'])
def criar():
    id_cliente = request.form.get('id_cliente', '')
    id_barbeiro = request.form.get('id_barbeiro', '')
    id_do_servico = request.form.get('id_do_servico', '')
    data = request.form.get('data', '').strip()
    hora = request.form.get('hora', '').strip()

    if not id_cliente or not id_barbeiro or not id_do_servico or not data or not hora:
        flash("Erro: Todos os campos do agendamento devem ser preenchidos!", "danger")
        return redirect(url_for('agendamentos.listar'))

    servico = Servico.query.get(id_do_servico)
    if not servico:
        flash("Erro: Serviço selecionado não existe!", "danger")
        return redirect(url_for('agendamentos.listar'))

    novo_agendamento = Agendamento(
        id_cliente=id_cliente,
        id_barbeiro=id_barbeiro,
        id_do_servico=id_do_servico,
        data_hora=f"{data} {hora}",
        valor_total=servico.preco,
        status_pagamento='Pendente',
    )
    db.session.add(novo_agendamento)
    db.session.commit()

    flash("Agendamento realizado com sucesso!", "success")
    return redirect(url_for('agendamentos.listar'))


# bgl de mudar status
@agendamentos_bp.route('/atualizar-status/<int:id_agendamento>', methods=['POST'])
def atualizar_status(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    agendamento.status_pagamento = 'Confirmado' if agendamento.status_pagamento == 'Pendente' else 'Pendente'
    db.session.commit()

    flash(f"Status do agendamento de '{agendamento.cliente.nome}' atualizado!", "info")
    return redirect(url_for('agendamentos.listar'))


# Excluir cliente q ja ta agendado
@agendamentos_bp.route('/deletar/<int:id_agendamento>', methods=['POST'])
def deletar(id_agendamento):
    agendamento = Agendamento.query.get_or_404(id_agendamento)
    db.session.delete(agendamento)
    db.session.commit()

    flash("Agendamento excluído com sucesso!", "info")
    return redirect(url_for('agendamentos.listar'))

# cadastrar cliente ai fio
@agendamentos_bp.route('/cadastrar-cliente', methods=['POST'])
def cadastrar_cliente():
    nome = request.form.get('nome', '').strip()
    telefone = request.form.get('telefone', '').strip()
    email = request.form.get('email', '').strip()

    if not nome or not telefone:
        flash("Erro: Nome e telefone são obrigatórios para cadastrar um cliente!", "danger")
        return redirect(url_for('agendamentos.listar'))

    novo_cliente = Cliente(nome=nome, telefone=telefone, email=email)
    db.session.add(novo_cliente)
    db.session.commit()

    flash(f"Cliente '{nome}' cadastrado com sucesso!", "success")
    return redirect(url_for('agendamentos.listar'))

    # Deletar cliente cadastrado (ficaria mt grande no <select>)
@agendamentos_bp.route('/deletar-cliente/<int:id_cliente>', methods=['POST'])
def deletar_cliente(id_cliente):
    cliente = Cliente.query.get_or_404(id_cliente)
    
    # Apaga tambem os agendamentos vinculados a esse cliente para nao dar erro no banco
    Agendamento.query.filter_by(id_cliente=id_cliente).delete()
    
    db.session.delete(cliente)
    db.session.commit()

    flash(f"Cliente '{cliente.nome}' e seus agendamentos foram excluídos!", "info")
    return redirect(url_for('agendamentos.listar'))