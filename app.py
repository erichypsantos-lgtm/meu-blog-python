import os
import json
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL", "sqlite:///blog.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "minha_chave_secreta_123")

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    imagem = db.Column(db.String(200), nullable=False)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def fazer_backup_json():
    posts = Post.query.order_by(Post.id.asc()).all()

    dados = []
    for post in posts:
        dados.append({
            "id": post.id,
            "titulo": post.titulo,
            "conteudo": post.conteudo,
            "imagem": post.imagem
        })

    with open("backup_posts.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

def criar_posts_padrao():
    if Post.query.count() == 0:
        posts_iniciais = [
            Post(
                titulo="Cloud Computing",
                conteudo="Aplicações de Cloud com Python, escalabilidade e servidores na nuvem.",
                imagem="images/cloud.jpg"
            ),
            Post(
                titulo="IoT com Python",
                conteudo="Internet das Coisas conecta dispositivos físicos usando sensores e automação.",
                imagem="images/iot.jpg"
            ),
            Post(
                titulo="Indústria 4.0",
                conteudo="Automação industrial com inteligência artificial e integração de sistemas.",
                imagem="images/industria.jpg"
            )
        ]
        db.session.add_all(posts_iniciais)
        db.session.commit()

def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logado"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return decorated_function

with app.app_context():
    db.create_all()
    criar_posts_padrao()
    fazer_backup_json()

@app.route("/")
def home():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("index.html", posts=posts)

@app.route("/post/<int:id>")
def post(id):
    post = Post.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        admin_user = os.getenv("ADMIN_USER", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "1234")

        if usuario == admin_user and senha == admin_password:
            session["admin_logado"] = True
            return redirect(url_for("home"))
        else:
            erro = "Usuário ou senha inválidos"

    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.pop("admin_logado", None)
    return redirect(url_for("home"))

@app.route("/novo", methods=["GET", "POST"])
@login_required
def novo_post():
    if request.method == "POST":
        titulo = request.form["titulo"]
        conteudo = request.form["conteudo"]
        arquivo = request.files.get("imagem")

        nome_arquivo = "images/cloud.jpg"

        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(caminho_arquivo)
            nome_arquivo = f"uploads/{nome_seguro}"

        novo = Post(
            titulo=titulo,
            conteudo=conteudo,
            imagem=nome_arquivo
        )

        db.session.add(novo)
        db.session.commit()
        fazer_backup_json()

        return redirect(url_for("home"))

    return render_template("novo_post.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_post(id):
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        post.titulo = request.form["titulo"]
        post.conteudo = request.form["conteudo"]

        arquivo = request.files.get("imagem")
        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(caminho_arquivo)
            post.imagem = f"uploads/{nome_seguro}"

        db.session.commit()
        fazer_backup_json()

        return redirect(url_for("home"))

    return render_template("editar_post.html", post=post)

@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    fazer_backup_json()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)