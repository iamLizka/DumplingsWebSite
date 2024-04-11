from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class RecipeForm(FlaskForm):
    name = StringField('Название')
    text = TextAreaField("Рецепт")
    time = StringField("Время приготовления")
    is_private = BooleanField("Личное")
    photo = FileField("")
    submit = SubmitField('Добавить')
