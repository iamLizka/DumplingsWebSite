from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash



class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), Length(min=8)])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Создать')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class EditForm(FlaskForm):
    name_edit = StringField('Имя:')
    surname_edit = StringField('Фамилия:')
    email_edit = EmailField('Почта:')
    password_old = PasswordField('старый пароль:')
    password_new = PasswordField('новый пароль:', validators=[Length(min=8)])
