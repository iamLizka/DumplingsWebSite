import os
import flask
import requests

from flask import Flask, render_template, redirect, make_response, url_for, request, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES
from urllib.parse import urlsplit
from data import db_session
from data.users import User
from data.recipes import Recipes
from forms.login import LoginForm
from forms.regist import RegisterForm
from forms.recipe import *


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] ='./static/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        return render_template('login.html', form=form, message='Неверная почта или пароль')
    return render_template('login.html', form=form)


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        level = request.form["level"]

        if form.email.data in [user.email for user in db_sess.query(User)]:
            form.email.data = ""
            return render_template('register.html', form=form, message='Такой пользователь уже существует')

        elif form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')

        else:
            user = User(name=form.name.data, surname=form.surname.data, email=form.email.data,
                        liked_recipes='', avatar='static/images/avatar_none.png', level=level)
            db_sess.add(user)
            user.set_password(form.password.data)
            db_sess.commit()
            login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home_user'))
    return render_template('register.html', form=form)


@app.route('/recipes')
def all_recipes():
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipes).filter(Recipes.is_private != True).order_by(Recipes.modified_date.desc()).all()
    list_liked_recipes = []
    if current_user.is_authenticated:
        list_liked_recipes = [int(i) for i in current_user.liked_recipes.split(',') if i != '']
    return render_template('recipes.html', recipes=recipes, list_recipes=list_liked_recipes)


@app.route('/my_recipes')
@login_required
def my_recipes():
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipes).filter(Recipes.user_id == current_user.id).order_by(Recipes.modified_date.desc()).all()
    list_liked_recipes = []
    if current_user.is_authenticated:
        list_liked_recipes = [int(i) for i in current_user.liked_recipes.split(',') if i != '']
    return render_template('recipes.html', recipes=recipes, add_recipes=True, list_recipes=list_liked_recipes)


@app.route('/read_recipe', methods=['POST'])
def read_recipe():
    db_sess = db_session.create_session()
    recipe_id = request.form['recipe']
    recipe = db_sess.query(Recipes).filter(Recipes.id == recipe_id).first()
    return render_template('read_recipe.html', recipe=recipe)


@app.route('/change_likes', methods=['POST'])
# @login_required
def change_likes():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        recipe_id = request.form['recipe_for_likes']
        recipe = db_sess.query(Recipes).filter(Recipes.id == recipe_id).first()

        if recipe_id not in current_user.liked_recipes.split(','):
            recipe.count_likes = int(recipe.count_likes) + 1
            recipe.users_likes = recipe.users_likes + str(current_user.id) + ','
            current_user.liked_recipes = current_user.liked_recipes + recipe_id + ','
        else:
            recipe.count_likes = int(recipe.count_likes) - 1
            recipe.users_likes = ','.join(recipe.users_likes.split(',')[0:-2]) + ','
            current_user.liked_recipes = ','.join(current_user.liked_recipes.split(',')[0:-2]) + ','

        db_sess.merge(current_user)
        db_sess.commit()
    return redirect(request.referrer)


@app.route('/create_recipes', methods=['GET', 'POST'])
@login_required
def create_recipes():
    form = RecipeForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        recipe = Recipes()
        recipe.name = form.name.data
        recipe.text = form.text.data
        recipe.time = form.time.data
        recipe.count_likes = 0
        recipe.users_likes = ''
        recipe.is_private = form.is_private.data

        if recipe.name == '':
            msg = 'Укажите название рецепта'
        elif recipe.time == '':
            msg = 'Укажите время приготовления'
        elif recipe.text == '':
            msg = 'Укажите рецепт'

        if recipe.name == '' or recipe.text == '' or recipe.time == '':
            return render_template('create_recipes.html', form=form, msg=msg)

        file = form.photo.data
        if file:
            filename = photos.save(file)
            recipe.photo = 'static/uploads/' + filename

        current_user.recipes.append(recipe)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(url_for('my_recipes'))

    return render_template('create_recipes.html', form=form)


@app.route('/restaurants', methods=['GET', 'POST'])
def restaurant():
    if request.method == 'POST':
        text = request.form['search_req']
    return render_template('restaurants.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile_user():
    form = RegisterForm()
    if request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if form.email_edit.data in [user.email for user in db_sess.query(User)]:
            form.email_edit.data = ""
            return render_template('edit_profile.html', form=form, message='Такой пользователь уже существует')

        elif form.password_new.data and form.password_old.data:
            if not user.check_password(form.password_old.data):
                return render_template('edit_profile.html', form=form, message='Неверный старый пароль')
            else:
                user.set_password(form.password_new.data)

        user.name = form.name_edit.data if form.name_edit.data else current_user.name
        user.surname = form.surname_edit.data if form.surname_edit.data else current_user.surname
        user.email = form.email_edit.data if form.email_edit.data else current_user.email
        user.avatar = request.form['img-avatar']
        user.level = request.form['level']
        db_sess.commit()
        return redirect(url_for('profile_user'))

    return render_template('edit_profile.html', form=form)


@app.route('/profile_user')
@login_required
def profile_user():
    return render_template('profile_user.html')


@app.route('/home')
@login_required
def home_user():
    return render_template('home_user.html')


@app.errorhandler(404)
def page_not_fount(error):
    res = make_response(f'Страница не найдена, но мы её найдем')
    return res

def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1', debug=True)



if __name__ == '__main__':
    main()
