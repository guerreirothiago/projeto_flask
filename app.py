from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
import urllib.request, json
import os

app = Flask(__name__)

app.secret_key = "chave_secreta"

# Lista para armazenar frutas e registros
frutas = []
registros = []

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização da extensão SQLAlchemy
db = SQLAlchemy(app)

# Modelo para os cursos
class Curso(db.Model):
    id = db.Column(Integer, primary_key=True)
    nome = db.Column(String(50))
    descricao = db.Column(String(100))
    ch = db.Column(Integer)

    def __init__(self, nome, descricao, ch):
        self.nome = nome
        self.descricao = descricao
        self.ch = ch

# Criação do banco de dados e das tabelas
with app.app_context():
    db.create_all()

# Rota principal
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        fruta = request.form.get("fruta")
        if fruta:
            frutas.append(fruta)
    return render_template("index.html", frutas=frutas)

# Rota para cursos
@app.route('/cursos', methods=["GET", "POST"])
def listar_cursos():
    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        ch = request.form.get("ch")
        if nome and descricao and ch:
            novo_curso = Curso(nome, descricao, int(ch))
            db.session.add(novo_curso)
            db.session.commit()
            return redirect(url_for('listar_cursos'))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    cursos = Curso.query.paginate(page=page, per_page=per_page)
    return render_template("cursos.html", cursos=cursos)

# Rota para criar cursos
@app.route('/criar_curso', methods=["GET", "POST"])
def criar_curso():
    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        ch = request.form.get("ch")
        if nome and descricao and ch:
            novo_curso = Curso(nome, descricao, int(ch))
            db.session.add(novo_curso)
            db.session.commit()
            return redirect(url_for('listar_cursos'))
    return render_template("novo_curso.html")

# Rota para deletar cursos
@app.route('/deletar_curso/<int:id>', methods=["GET", "POST"])
def deletar_curso(id):
    curso = Curso.query.get(id)
    if curso:
        db.session.delete(curso)
        db.session.commit()
    return redirect(url_for('listar_cursos'))

# Rota para atualizar cursos
@app.route('/atualizar_curso/<int:id>', methods=["GET", "POST"])
def atualizar_curso(id):
    curso = Curso.query.get(id)
    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        ch = request.form.get("ch")
        if not nome or not descricao or not ch:
            flash("Preencha todos os campos")
        else:
            curso.nome = nome
            curso.descricao = descricao
            curso.ch = int(ch)
            db.session.commit()
            return redirect(url_for("listar_cursos"))
    return render_template("atualizar_curso.html", curso=curso)

# Rota para sobre
@app.route('/sobre', methods=["GET", "POST"])
def sobre():
    if request.method == "POST":
        aluno = request.form.get("aluno")
        nota = request.form.get("nota")
        if aluno and nota:
            registros.append({"aluno": aluno, "nota": nota})
    return render_template("sobre.html", registros=registros)

# Rota para filmes
@app.route('/filmes', methods=['GET'])
def filmes():
    propiedade = request.args.get('propiedade', 'mais_populares')
    
    if propiedade == "mais_populares":
        h2 = "Mais Populares"
    elif propiedade == "kids":
        h2 = "Filmes para Crianças"
    elif propiedade == "2020":
        h2 = "Filmes de 2020"
    elif propiedade == "drama":
        h2 = "Filmes de Drama"
    elif propiedade == "tom_cruise":
        h2 = "Filmes de Tom Cruise"
    else:
        h2 = propiedade

    api_key = "6883a2f6c2f2b580a305ebbb49c7d397"
    base_url = "https://api.themoviedb.org/3/discover/movie"
    url_params = {
        "sort_by": "popularity.desc",
        "api_key": api_key
    }

    if propiedade == "kids":
        url_params["certification_country"] = "US"
        url_params["certification.lte"] = "G"
    elif propiedade == "2020":
        url_params["primary_release_year"] = "2020"
    elif propiedade == "drama":
        url_params["with_genres"] = "18"
    elif propiedade == "tom_cruise":
        url_params["with_genres"] = "28"

    url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in url_params.items()])}"

    resposta = urllib.request.urlopen(url)
    dados = resposta.read()
    jsondata = json.loads(dados)

    return render_template("filmes.html", filmes=jsondata["results"], propiedade=propiedade)

if __name__ == '__main__':
    app.run(debug=True)
