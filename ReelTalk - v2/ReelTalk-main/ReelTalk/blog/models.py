# models.py
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(150), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    niver = db.Column(db.Date, nullable=True)
    eh_administrador = db.Column(db.Boolean, default=False)
    postagens = db.relationship('Postagem', backref='autor', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Postagem(db.Model):
    __tablename__ = 'postagens'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    review = db.Column(db.Text, nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    comentarios = db.relationship('Comentario', backref='postagem', lazy=True, cascade="all, delete-orphan")

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    postagem_id = db.Column(db.Integer, db.ForeignKey('postagens.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    