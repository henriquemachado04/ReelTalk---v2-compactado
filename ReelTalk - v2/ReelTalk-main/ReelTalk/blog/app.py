from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ContatoForm, PostagemForm

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column(db.String(80), nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    niver = db.Column(db.String(10))
    eh_administrador = db.Column(db.Boolean, default=True)
    postagens = db.relationship("Postagem", back_populates="usuario")
    comentarios = db.relationship("Comentario", back_populates="usuario")

class Postagem(db.Model):
    __tablename__ = "postagens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    review = db.Column(db.String, nullable=False)
    imagem_url = StringField('URL da Imagem', validators=[DataRequired(), URL()])
    nota = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship("Usuario", back_populates="postagens")
    comentarios = db.relationship("Comentario", back_populates="postagem")

class Comentario(db.Model):
    __tablename__ = "comentarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conteudo = db.Column(db.String, nullable=False)
    postagem_id = db.Column(db.Integer, db.ForeignKey('postagens.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship("Usuario", back_populates="comentarios")
    postagem = db.relationship("Postagem", back_populates="comentarios")

def CriaUsuario(nome, nome_usuario, senha, email, niver):
    usuario = Usuario(nome_usuario=nome_usuario, nome=nome, senha=senha, email=email, niver=niver)
    db.session.add(usuario)
    db.session.commit()

def CriaPostagem(titulo, review, nota, usuario_id):
    postagem = Postagem(titulo=titulo, review=review, nota=nota, imagem_url = request.form.get('imagem_url'), usuario_id=usuario_id)
    db.session.add(postagem)
    db.session.commit()
    return postagem

def CriaComentario(conteudo, postagem_id, usuario_id):
    comentario = Comentario(conteudo=conteudo, postagem_id=postagem_id,  usuario_id=usuario_id)
    db.session.add(comentario)
    db.session.commit()

def DeletarPostagem(postagem_id):
    postagem = Postagem.query.get(postagem_id)
    if postagem:
        db.session.delete(postagem)
        db.session.commit()

def DeletarComentario(comentario_id):
    comentario = Comentario.query.get(comentario_id)
    if comentario:
        db.session.delete(comentario)
        db.session.commit()

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = ContatoForm()
    if form.validate_on_submit():
        senha_hash = generate_password_hash(form.senha.data)
        novo_usuario = Usuario(
            nome_usuario=form.nome_usuario.data,
            nome=form.nome.data,
            senha=senha_hash,
            email=form.email.data,
            niver=form.niver.data
        )
        CriaUsuario(novo_usuario.nome, novo_usuario.nome_usuario, novo_usuario.senha, novo_usuario.email, novo_usuario.niver)
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    return render_template('cadastro.html', formulario=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['nome_usuario'] = user.nome_usuario
            session['eh_administrador'] = user.eh_administrador
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        flash('Falha no login. Verifique seu email ou senha.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    postagens = Postagem.query.all()
    return render_template('index.html', postagens=postagens)

@app.route('/criar_postagem', methods=['GET', 'POST'])
def criar_postagem():
    form = PostagemForm()  
    if form.validate_on_submit():
        titulo = form.titulo.data
        review = form.review.data
        nota = form.nota.data
        usuario_id = session.get('usuario_id')

        nova_postagem = Postagem(titulo=titulo, review=review, nota=nota, usuario_id=usuario_id)
        db.session.add(nova_postagem)
        db.session.commit()

        flash('Postagem criada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('criar_postagem.html', form=form)

@app.route('/postagem/<int:postagem_id>', methods=['GET', 'POST'])
def detalhe_postagem(postagem_id):
    postagem = Postagem.query.get(postagem_id)
    comentarios = Comentario.query.filter_by(postagem_id=postagem_id).all()

    if request.method == 'POST':
        conteudo = request.form['conteudo']
        usuario_id = session.get('usuario_id')

        novo_comentario = Comentario(conteudo=conteudo, postagem_id=postagem_id, usuario_id=usuario_id)
        db.session.add(novo_comentario)
        db.session.commit()

        flash('Comentário adicionado com sucesso!', 'success')
        return redirect(url_for('detalhe_postagem', postagem_id=postagem_id))

    return render_template('detalhe_postagem.html', postagem=postagem, comentarios=comentarios)

@app.route('/excluir_postagem/<int:postagem_id>')
def excluir_postagem(postagem_id):
    usuario_id = session.get('usuario_id')
    postagem = Postagem.query.get(postagem_id)

    if postagem and (postagem.usuario_id == usuario_id or session.get('eh_administrador')):
        db.session.delete(postagem)
        db.session.commit()
        flash('Postagem excluída com sucesso!', 'success')
    else:
        flash('Você não tem permissão para excluir esta postagem.', 'danger')

    return redirect(url_for('index'))

@app.route('/excluir_comentario/<int:comentario_id>')
def excluir_comentario(comentario_id):
    usuario_id = session.get('usuario_id')
    comentario = Comentario.query.get(comentario_id)

    if comentario and (comentario.usuario_id == usuario_id or session.get('eh_administrador')):
        db.session.delete(comentario)
        db.session.commit()
        flash('Comentário excluído com sucesso!', 'success')
    else:
        flash('Você não tem permissão para excluir este comentário.', 'danger')

    return redirect(url_for('detalhe_postagem', postagem_id=comentario.postagem_id))

@app.route('/editar_postagem/<int:postagem_id>', methods=['GET', 'POST'])
def editar_postagem(postagem_id):
    postagem = Postagem.query.get(postagem_id)
    usuario_id = session.get('usuario_id')

    if postagem is None or (postagem.usuario_id != usuario_id and not session.get('eh_administrador')):
        flash('Você não tem permissão para editar esta postagem.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        postagem.titulo = request.form['titulo']
        postagem.review = request.form['review']
        postagem.nota = request.form['nota']
        db.session.commit()

        flash('Postagem editada com sucesso!', 'success')
        return redirect(url_for('detalhe_postagem', postagem_id=postagem.id))

    return render_template('editar_postagem.html', postagem=postagem)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)