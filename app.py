from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "barbearia_alpha_secret_key"

# Banco de dados em memória (Lista de Dicionários)
agendamentos = [
    {"id": 1, "cliente": "Carlos Silva", "servico": "Corte e Barba", "preco": 70.0, "status": "Confirmado"},
    {"id": 2, "cliente": "Lucas Mendes", "servico": "Corte Social", "preco": 40.0, "status": "Pendente"},
    {"id": 3, "cliente": "Rafael Lima", "servico": "Barboterapia", "preco": 50.0, "status": "Confirmado"}
]
proximo_id = 4

@app.route('/', methods=['GET'])
def index():
    busca = request.args.get('busca', '').strip().lower()
    
    # Campo de Busca / Filtro (GET)
    if busca:
        agendamentos_filtrados = [
            a for a in agendamentos 
            if busca in a['cliente'].lower() or busca in a['servico'].lower()
        ]
    else:
        agendamentos_filtrados = agendamentos

    # Dashboard / Cards de Métricas (Calculados Dinamicamente)
    total_agendamentos = len(agendamentos)
    confirmados = sum(1 for a in agendamentos if a['status'] == 'Confirmado')
    pendentes = sum(1 for a in agendamentos if a['status'] == 'Pendente')
    faturamento_total = sum(a['preco'] for a in agendamentos if a['status'] == 'Confirmado')

    return render_template(
        'index.html', 
        agendamentos=agendamentos_filtrados,
        total_agendamentos=total_agendamentos,
        confirmados=confirmados,
        pendentes=pendentes,
        faturamento_total=faturamento_total,
        busca=busca
    )

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    global proximo_id
    
    cliente = request.form.get('cliente', '').strip()
    servico = request.form.get('servico', '').strip()
    preco_raw = request.form.get('preco', '').strip()

    # Validação de Back-end: Campos Vazios
    if not cliente or not servico or not preco_raw:
        flash("Erro: Todos os campos do agendamento devem ser preenchidos!", "danger")
        return redirect(url_for('index'))

    # Validação de Back-end: Preço Negativo ou Zerado
    try:
        preco = float(preco_raw)
        if preco <= 0:
            flash("Erro: O valor do serviço deve ser maior que zero!", "danger")
            return redirect(url_for('index'))
    except ValueError:
        flash("Erro: Insira um preço válido!", "danger")
        return redirect(url_for('index'))

    # Cadastro de item válido
    novo_agendamento = {
        "id": proximo_id,
        "cliente": cliente,
        "servico": servico,
        "preco": preco,
        "status": "Pendente"
    }
    agendamentos.append(novo_agendamento)
    proximo_id += 1

    flash("Agendamento realizado com sucesso!", "success")
    return redirect(url_for('index'))

@app.route('/alterar-status/<int:id_agendamento>', methods=['POST'])
def alterar_status(id_agendamento):
    # Alteração de Estado do Registro
    for a in agendamentos:
        if a['id'] == id_agendamento:
            a['status'] = 'Confirmado' if a['status'] == 'Pendente' else 'Pendente'
            flash(f"Status do agendamento de '{a['cliente']}' atualizado!", "info")
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)