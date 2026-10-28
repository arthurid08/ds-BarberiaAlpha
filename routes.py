import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
from sqlalchemy import or_
from database import db
from models import Agendamento, Cliente, Barbeiro, Servico, Usuario
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

agendamentos_bp = Blueprint('agendamentos', __name__)

# Extensões de imagem permitidas
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'webp'}

def extensao_permitida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

@agendamentos_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            
            cliente = Cliente.query.filter_by(id_usuario=usuario.id).first()
            if not cliente and usuario.tipo_acesso == 'cliente':
                cliente = Cliente(id_usuario=usuario.id, nome=usuario.username, email=usuario.email, telefone=usuario.telefone or '')
                db.session.add(cliente)
                db.session.commit()

            session['user_id'] = usuario.id
            session['user_nome'] = cliente.nome if cliente else usuario.username
            session['user_email'] = cliente.email if cliente else usuario.email
            session['user_telefone'] = cliente.telefone if cliente else (usuario.telefone or '')
            
            flash(f"Bem-vindo(a), {usuario.username}!", "success")
            return redirect(url_for('agendamentos.listar'))
        else:
            flash("E-mail ou senha incorretos.", "danger")
            
    return render_template('login.html')

@agendamentos_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha', '').strip()
        
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("E-mail já cadastrado! Faça login com suas credenciais.", "danger")
            return redirect(url_for('agendamentos.login'))

        # Processamento e validação da imagem de perfil
        nome_arquivo_foto = 'padrao.png'  # Valor padrão caso não envie foto
        
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '':
                if extensao_permitida(file.filename):
                    filename_seguro = secure_filename(file.filename)
                    ext = filename_seguro.rsplit('.', 1)[1].lower()
                    nome_arquivo_foto = f"{uuid.uuid4().hex}.{ext}"
                    caminho_salvamento = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_arquivo_foto)
                    file.save(caminho_salvamento)
                else:
                    flash("Extensão de imagem não permitida! Envie arquivos PNG, JPG, JPEG ou WEBP.", "danger")
                    return redirect(url_for('agendamentos.cadastro'))
        
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(
            username=nome,
            email=email,
            telefone=telefone,
            senha=senha_hash,
            tipo_acesso='cliente',
            foto=nome_arquivo_foto
        )
        db.session.add(novo_usuario)
        db.session.commit()

        novo_cliente = Cliente(
            id_usuario=novo_usuario.id,
            nome=nome,
            telefone=telefone,
            email=email
        )
        db.session.add(novo_cliente)
        db.session.commit()
        
        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for('agendamentos.login'))
        
    return render_template('cadastro.html')

@agendamentos_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Sua sessão foi encerrada.", "info")
    return redirect(url_for('agendamentos.listar'))

@agendamentos_bp.route('/', methods=['GET'])
def listar():
    termo_busca = request.args.get('busca', '').strip()

    agendamentos = []
    if current_user.is_authenticated and current_user.tipo_acesso == 'admin':
        consulta = Agendamento.query.filter_by(ativo=True).join(Cliente).join(Servico)
        if termo_busca:
            consulta = consulta.filter(
                or_(
                    Cliente.nome.ilike(f'%{termo_busca}%'),
                    Servico.nome_do_servico.ilike(f'%{termo_busca}%')
                )
            )
        agendamentos = consulta.order_by(Agendamento.id_do_agendamento.desc()).all()

    todos = Agendamento.query.all()
    total_agendamentos = sum(1 for a in todos if a.ativo)
    confirmados = sum(1 for a in todos if a.ativo and a.status_pagamento == 'Confirmado')
    pendentes = sum(1 for a in todos if a.ativo and a.status_pagamento == 'Pendente')
    faturamento_total = float(sum(a.valor_total for a in todos if a.ativo and a.status_pagamento == 'Confirmado'))

    horarios_disponiveis = [
        "08:00", "09:00", "10:00", "11:00", "12:00",
        "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
    ]

    meus_agendamentos = []
    if current_user.is_authenticated and current_user.tipo_acesso == 'cliente':
        cliente = Cliente.query.filter_by(id_usuario=current_user.id).first()
        if cliente:
            meus_agendamentos = Agendamento.query.filter_by(id_cliente=cliente.id_cliente, ativo=True)\
                .order_by(Agendamento.id_do_agendamento.desc()).all()

    return render_template(
        'index.html',
        agendamentos=agendamentos,
        meus_agendamentos=meus_agendamentos,
        barbeiros=Barbeiro.query.order_by(Barbeiro.nome).all(),
        servicos=Servico.query.order_by(Servico.nome_do_servico).all(),
        total_agendamentos=total_agendamentos,
        confirmados=confirmados,
        pendentes=pendentes,
        faturamento_total=faturamento_total,
        busca=termo_busca,
        horarios_disponiveis=horarios_disponiveis
    )

@agendamentos_bp.route('/horarios-ocupados', methods=['GET'])
def horarios_ocupados():
    data = request.args.get('data', '').strip()
    id_barbeiro = request.args.get('id_barbeiro', '').strip()

    if not data or not id_barbeiro or not id_barbeiro.isdigit():
        return jsonify([])

    agendamentos = Agendamento.query.filter(
        Agendamento.id_barbeiro == int(id_barbeiro),
        Agendamento.data_hora.like(f"{data}%"),
        Agendamento.ativo == True
    ).all()

    ocupados = [a.data_hora.split(' ')[1].strip() for a in agendamentos if len(a.data_hora.split(' ')) > 1]
    return jsonify(ocupados)

@agendamentos_bp.route('/criar', methods=['POST'])
@login_required
def criar():
    cliente = Cliente.query.filter_by(id_usuario=current_user.id).first()
    if not cliente:
        cliente = Cliente(
            id_usuario=current_user.id,
            nome=current_user.username,
            telefone=current_user.telefone or '',
            email=current_user.email
        )
        db.session.add(cliente)
        db.session.flush()

    id_barbeiro = request.form.get('barbeiro', '')
    id_do_servico = request.form.get('servico', '')
    data = request.form.get('data', '').strip()
    hora = request.form.get('horario', '').strip()

    if not id_barbeiro or not id_do_servico or not data or not hora:
        flash("Erro: Preencha todos os campos obrigatórios para agendar!", "danger")
        return redirect(url_for('agendamentos.listar'))

    try:
        data_selecionada = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        flash("Erro: Formato de data inválido!", "danger")
        return redirect(url_for('agendamentos.listar'))

    hoje = datetime.now().date()
    if data_selecionada < hoje:
        flash("Erro: Não é possível realizar agendamentos em datas passadas!", "danger")
        return redirect(url_for('agendamentos.listar'))

    data_hora_str = f"{data} {hora}"
    conflito = Agendamento.query.filter_by(id_barbeiro=id_barbeiro, data_hora=data_hora_str, ativo=True).first()
    if conflito:
        flash("Erro: Esse horário já foi agendado para este barbeiro!", "danger")
        return redirect(url_for('agendamentos.listar'))

    servico = Servico.query.get(id_do_servico)
    if not servico:
        flash("Erro: Serviço selecionado é inválido!", "danger")
        return redirect(url_for('agendamentos.listar'))

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

    flash("Agendamento realizado com sucesso!", "success")
    return redirect(url_for('agendamentos.listar'))

@agendamentos_bp.route('/cancelar/<int:id_agendamento>', methods=['GET', 'POST'])
@login_required
def cancelar_cliente(id_agendamento):
    if request.method == 'GET':
        return redirect(url_for('agendamentos.listar'))

    agendamento = Agendamento.query.get_or_404(id_agendamento)
    cliente = Cliente.query.filter_by(id_usuario=current_user.id).first()

    if not cliente or (agendamento.id_cliente != cliente.id_cliente and current_user.tipo_acesso != 'admin'):
        flash("Acesso negado: Você só pode cancelar os seus próprios agendamentos.", "danger")
        return redirect(url_for('agendamentos.listar'))

    agendamento.ativo = False
    db.session.commit()

    flash("Seu agendamento foi cancelado com sucesso!", "info")
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

@agendamentos_bp.route('/deletar/<int:id_agendamento>', methods=['POST'])
@login_required
def deletar(id_agendamento):
    if current_user.tipo_acesso != 'admin':
        flash("Acesso negado: Apenas administradores podem excluir agendamentos.", "danger")
        return redirect(url_for('agendamentos.listar'))

    agendamento = Agendamento.query.get_or_404(id_agendamento)
    agendamento.ativo = False
    db.session.commit()

    flash("Agendamento removido da lista!", "info")
    return redirect(url_for('agendamentos.listar'))