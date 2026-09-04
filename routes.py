from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from database import db
from models import Agendamento, Cliente, Barbeiro, Servico, Usuario
from flask_login import login_user, logout_user, login_required, current_user

agendamentos_bp = Blueprint('agendamentos', __name__)

# Rota de Login (Apenas Admin)
@agendamentos_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        senha = request.form.get('senha', '').strip()

        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.senha == senha and user.tipo_acesso == 'admin':
            login_user(user)
            flash("Bem-vindo(a) ao painel administrativo!", "success")
            return redirect(url_for('agendamentos.listar'))
        else:
            flash("Usuário ou senha de administrador incorretos!", "danger")

    return render_template('login.html')

# Rota de Logout
@agendamentos_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Sua sessão de administrador foi encerrada.", "info")
    return redirect(url_for('agendamentos.listar'))

# Página Principal (Acesso público para clientes)
@agendamentos_bp.route('/', methods=['GET'])
def listar():
    termo_busca = request.args.get('busca', '').strip()

    # Tabela exibe apenas os agendamentos ativos
    consulta = Agendamento.query.filter_by(ativo=True).join(Cliente).join(Servico)

    if termo_busca:
        consulta = consulta.filter(
            db.or_(
                Cliente.nome.ilike(f'%{termo_busca}%'),
                Servico.nome_do_servico.ilike(f'%{termo_busca}%')
            )
        )

    agendamentos = consulta.order_by(Agendamento.id_do_agendamento.desc()).all()

    # Cálculo de métricas e Faturamento Mantido
    todos_agendamentos = Agendamento.query.all()
    
    total_agendamentos = sum(1 for a in todos_agendamentos if a.ativo)
    confirmados = sum(1 for a in todos_agendamentos if a.ativo and a.status_pagamento == 'Confirmado')
    pendentes = sum(1 for a in todos_agendamentos if a.ativo and a.status_pagamento == 'Pendente')
    
    # Soma de TODOS os confirmados (mesmo os excluídos logicamente)
    faturamento_total = float(sum(a.valor_total for a in todos_agendamentos if a.status_pagamento == 'Confirmado'))

    horarios_disponiveis = [
        "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
    ]

    agendamento_sucesso = None
    ultimo_id = session.get('ultimo_agendamento_id')
    if ultimo_id:
        agendamento_sucesso = Agendamento.query.get(ultimo_id)

    return render_template(
        'INDEX.html',
        agendamentos=agendamentos,
        barbeiros=Barbeiro.query.order_by(Barbeiro.nome).all(),
        servicos=Servico.query.order_by(Servico.nome_do_servico).all(),
        total_agendamentos=total_agendamentos,
        confirmados=confirmados,
        pendentes=pendentes,
        faturamento_total=faturamento_total,
        busca=termo_busca,
        horarios_disponiveis=horarios_disponiveis,
        agendamento_sucesso=agendamento_sucesso
    )

@agendamentos_bp.route('/horarios-ocupados', methods=['GET'])
def horarios_ocupados():
    data = request.args.get('data', '').strip()
    id_barbeiro = request.args.get('id_barbeiro', '').strip()

    if not data or not id_barbeiro:
        return jsonify([])

    # Busca agendamentos do barbeiro na data selecionada
    agendamentos = Agendamento.query.filter(
        Agendamento.id_barbeiro == int(id_barbeiro),
        Agendamento.data_hora.like(f"{data}%"),
        Agendamento.ativo == True
    ).all()

    # Extrai o horário no formato HH:MM do campo data_hora ("YYYY-MM-DD HH:MM")
    ocupados = []
    for a in agendamentos:
        partes = a.data_hora.split(' ')
        if len(partes) > 1:
            ocupados.append(partes[1].strip())

    return jsonify(ocupados)

# Criar Agendamento
@agendamentos_bp.route('/criar', methods=['POST'])
def criar():
    nome_cliente = request.form.get('nome_cliente', '').strip()
    telefone_cliente = request.form.get('telefone_cliente', '').strip()
    email_cliente = request.form.get('email_cliente', '').strip()

    id_barbeiro = request.form.get('id_barbeiro', '')
    id_do_servico = request.form.get('id_do_servico', '')
    data = request.form.get('data', '').strip()
    hora = request.form.get('hora', '').strip()

    if not nome_cliente or not telefone_cliente or not id_barbeiro or not id_do_servico or not data or not hora:
        flash("Erro: Todos os campos obrigatórios devem ser preenchidos!", "danger")
        return redirect(url_for('agendamentos.listar'))

    data_hora_str = f"{data} {hora}"
    conflito = Agendamento.query.filter_by(id_barbeiro=id_barbeiro, data_hora=data_hora_str, ativo=True).first()
    if conflito:
        flash("Erro: Esse horário já foi agendado para este barbeiro!", "danger")
        return redirect(url_for('agendamentos.listar'))

    servico = Servico.query.get(id_do_servico)
    if not servico:
        flash("Erro: Serviço selecionado não existe!", "danger")
        return redirect(url_for('agendamentos.listar'))

    cliente = Cliente.query.filter_by(telefone=telefone_cliente).first()
    if not cliente:
        cliente = Cliente(nome=nome_cliente, telefone=telefone_cliente, email=email_cliente)
        db.session.add(cliente)
        db.session.flush()

    novo_agendamento = Agendamento(
        id_cliente=cliente.id_cliente,
        id_barbeiro=id_barbeiro,
        id_do_servico=id_do_servico,
        data_hora=data_hora_str,
        valor_total=servico.preco,
        status_pagamento='Pendente',
        ativo=True
    )
    db.session.add(novo_agendamento)
    db.session.commit()

    session['ultimo_agendamento_id'] = novo_agendamento.id_do_agendamento

    flash("Agendamento realizado com sucesso!", "success")
    return redirect(url_for('agendamentos.listar'))

@agendamentos_bp.route('/atualizar-status/<int:id_agendamento>', methods=['POST'])
@login_required
def atualizar_status(id_agendamento):
    if current_user.tipo_acesso != 'admin':
        flash("Acesso negado: Apenas administradores podem alterar o status.", "danger")
        return redirect(url_for('agendamentos.listar'))

    agendamento = Agendamento.query.get_or_404(id_agendamento)
    agendamento.status_pagamento = 'Confirmado' if agendamento.status_pagamento == 'Pendente' else 'Pendente'
    db.session.commit()

    flash(f"Status do agendamento de '{agendamento.cliente.nome}' atualizado!", "info")
    return redirect(url_for('agendamentos.listar'))

# Soft Delete (Desativa mantendo o faturamento)
@agendamentos_bp.route('/deletar/<int:id_agendamento>', methods=['POST'])
@login_required
def deletar(id_agendamento):
    if current_user.tipo_acesso != 'admin':
        flash("Acesso negado: Apenas administradores podem excluir agendamentos.", "danger")
        return redirect(url_for('agendamentos.listar'))

    agendamento = Agendamento.query.get_or_404(id_agendamento)
    agendamento.ativo = False
    db.session.commit()

    flash("Agendamento removido da lista! O faturamento foi mantido.", "info")
    return redirect(url_for('agendamentos.listar'))