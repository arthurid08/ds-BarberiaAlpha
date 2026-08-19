from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/agendamento")
def agendamento():
    return render_template("agendamento.html")

@app.route("/confirmar", methods=["POST"])
def confirmar():
    nome = request.form.get("nome")
    telefone = request.form.get("telefone")
    servico = request.form.get("servico")
    barbeiro = request.form.get("barbeiro")
    data = request.form.get("data")
    hora = request.form.get("hora")

    return render_template(
        "confirmacao.html",
        nome=nome,
        telefone=telefone,
        servico=servico,
        barbeiro=barbeiro,
        data=data,
        hora=hora
    )

if __name__ == "__main__":
    app.run(debug=True)