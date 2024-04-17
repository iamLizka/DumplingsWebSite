from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FileField
from main import photos


class RecipeForm(FlaskForm):
    name = StringField('Название')
    text = TextAreaField("Рецепт")
    time = StringField("Время приготовления")
    is_private = BooleanField("Личное")
    photo = FileField(validators=[FileAllowed(photos, "Допустимый формат: 'PNG', 'JPG', 'JPEG', 'GIF'")])
    submit = SubmitField('Добавить')
