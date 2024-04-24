import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    count_likes = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users_likes = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    recipe_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("recipes.id"))

    user = orm.relationship('User')
    recipe = orm.relationship('Recipes')