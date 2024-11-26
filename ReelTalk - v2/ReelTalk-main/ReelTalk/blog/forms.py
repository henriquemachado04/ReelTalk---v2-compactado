from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, DateField, PasswordField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, Length, URL

class ContatoForm(FlaskForm):
    nome_usuario = StringField(
        'Nome do Usuário',
        validators=[DataRequired(message="O campo de nome do usuário é obrigatório.")]
    )
    nome = StringField(
        'Nome',
        validators=[
            DataRequired(message="O campo nome é obrigatório."),
            Length(min=2, max=50, message="O nome deve ter entre 2 e 50 caracteres.")
        ]
    )
    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(message="O campo de senha é obrigatório."),
            Length(min=6, message="A senha deve ter pelo menos 6 caracteres.")
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="O campo de email é obrigatório."),
            Email(message="Digite um endereço de email válido.")
        ]
    )
    niver = DateField(
        'Data de Nascimento',
        format='%Y-%m-%d',
        validators=[DataRequired(message="O campo de data de nascimento é obrigatório.")],
        render_kw={"placeholder": "Ex.: 1990-01-01"}
    )
    enviar = SubmitField('Enviar')

class PostagemForm(FlaskForm):
    titulo = StringField(
        "Título",
        validators=[DataRequired(message="O campo título é obrigatório.")]
    )
    review = TextAreaField(
        "Review",
        validators=[
            DataRequired(message="O campo review é obrigatório."),
            Length(min=15, message="O review deve ter pelo menos 15 caracteres.")
        ]
    )
    nota = IntegerField(
        "Nota",
        validators=[
            DataRequired(message="O campo nota é obrigatório."),
            NumberRange(min=0, max=5, message="A nota deve ser entre 0 e 5.")
        ]
    )
    imagem_url = StringField(
        'URL da Imagem',
        validators=[
            DataRequired(message="A URL da imagem é obrigatória."),
            URL(message="Digite uma URL válida para a imagem.")
        ]
    )
    enviar = SubmitField('Criar Postagem')
