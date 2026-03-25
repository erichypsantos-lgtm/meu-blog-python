import os
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['SECRET_KEY'] = 'minha_chave_secreta_123'

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    imagem = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None

    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if usuario == 'admin' and senha == '1234':
            session['admin_logado'] = True
            return redirect(url_for('home'))
        else:
            erro = 'Usuário ou senha inválidos'

    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('admin_logado', None)
    return redirect(url_for('home'))

@app.route('/novo', methods=['GET', 'POST'])
@login_required
def novo_post():
    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        arquivo = request.files['imagem']

        nome_arquivo = 'uploads/padrao.jpg'

        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
            arquivo.save(caminho_arquivo)
            nome_arquivo = f'uploads/{nome_seguro}'

        novo = Post(titulo=titulo, conteudo=conteudo, imagem=nome_arquivo)
        db.session.add(novo)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('novo_post.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_post(id):
    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        post.titulo = request.form['titulo']
        post.conteudo = request.form['conteudo']

        arquivo = request.files['imagem']
        if arquivo and arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
            arquivo.save(caminho_arquivo)
            post.imagem = f'uploads/{nome_seguro}'

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('editar_post.html', post=post)

@app.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)