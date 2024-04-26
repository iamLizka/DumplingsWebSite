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
from data.comments import Comments
from forms.login import LoginForm
from forms.regist import RegisterForm, EditForm
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
    return render_template('home.html', home=True)


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
    return render_template('recipes.html', title='Рецепты', recipes=recipes, list_recipes=list_liked_recipes, db_sess=db_sess, user=User)


@app.route('/like_recipes')
@login_required
def like_recipes():
    db_sess = db_session.create_session()
    list_liked_recipes = [int(i) for i in current_user.liked_recipes.split(',') if i != '']
    recipes = db_sess.query(Recipes).filter(Recipes.id.in_(list_liked_recipes)).order_by(Recipes.modified_date.desc()).all()
    return render_template('recipes.html', title='Понравившиеся рецепты', recipes=recipes, list_recipes=list_liked_recipes, db_sess=db_sess, user=User)


@app.route('/my_recipes')
@login_required
def my_recipes():
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipes).filter(Recipes.user_id == current_user.id).order_by(Recipes.modified_date.desc()).all()
    list_liked_recipes = [int(i) for i in current_user.liked_recipes.split(',') if i != '']
    return render_template('recipes.html', recipes=recipes, title='Мои рецепты', add_recipes=True, list_recipes=list_liked_recipes, db_sess=db_sess, user=User)


@app.route('/profile_user_recipe/<int:id>', methods=['POST'])
def profile_user_recipe(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    return render_template('profile_user.html', authenticated=False, title=user.name, user=user)


@app.route('/write_comment/<int:id>', methods=['POST'])
@login_required
def write_comment(id):
    comment = request.form['comment']
    if comment:
        db_sess = db_session.create_session()
        create_comment = Comments(comment=comment, count_likes=0, users_likes='',user_id=current_user.id, recipe_id=id)
        db_sess.add(create_comment)
        db_sess.commit()
    return redirect(url_for('read_recipe', id=id))


@app.route('/read_recipe/<int:id>', methods=['GET','POST'])
def read_recipe(id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipes).filter(Recipes.id == id).first()
    comments = db_sess.query(Comments).filter(Comments.recipe_id == id).order_by(Comments.modified_date.desc()).all()
    user_name = db_sess.query(User).filter(User.id == recipe.user_id).first().name
    list_liked_recipes = []
    if current_user.is_authenticated:
        list_liked_recipes = [int(i) for i in current_user.liked_recipes.split(',') if i != '']
    return render_template('read_recipe.html', recipe=recipe, user_name=user_name,  user=User, db_sess=db_sess, comments=comments, list_recipes=list_liked_recipes)


@app.route('/change_likes', methods=['POST'])
@login_required
def change_likes():
    db_sess = db_session.create_session()
    recipe_id = request.form['recipe_for_likes']
    recipe = db_sess.query(Recipes).filter(Recipes.id == recipe_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()

    if recipe_id not in user.liked_recipes.split(','):
        recipe.count_likes = int(recipe.count_likes) + 1
        recipe.users_likes = recipe.users_likes + str(user.id) + ','
        user.liked_recipes = user.liked_recipes + recipe_id + ','
    else:
        recipe.count_likes = int(recipe.count_likes) - 1
        users_likes = recipe.users_likes.split(',')
        users_likes = [u for u in users_likes if u != '']
        users_likes.remove(str(user.id))
        recipe.users_likes = ','.join(users_likes) + ','
        liked_recipes = current_user.liked_recipes.split(',')
        liked_recipes.remove(recipe_id)
        liked_recipes = [r for r in liked_recipes if r != '']
        user.liked_recipes = ','.join(liked_recipes) + ','

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
        recipe.ingredients = form.ingredients.data
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
        elif recipe.ingredients == '':
            msg = 'Укажите ингредиенты'

        if recipe.name == '' or recipe.text == '' or recipe.time == '' or recipe.ingredients == '':
            return render_template('create_recipes.html', form=form, msg=msg)

        file = form.photo.data
        if file:
            filename = photos.save(file)
            recipe.photo = '/static/uploads/' + filename

        current_user.recipes.append(recipe)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(url_for('my_recipes'))

    return render_template('create_recipes.html', form=form, title='Создание рецепта')


@app.route('/recipe_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    form = RecipeForm()
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipes).filter(Recipes.id == id).first()

    if request.method == "GET":
        if recipe:
            form.name.data = recipe.name
            form.text.data = recipe.text
            form.time.data = recipe.time
            form.ingredients.data = recipe.ingredients
            form.is_private.data = recipe.is_private

    if form.validate_on_submit():
        if recipe:
            recipe.name = form.name.data
            recipe.text = form.text.data
            recipe.time = form.time.data
            recipe.ingredients = form.ingredients.data
            recipe.is_private = form.is_private.data
            file = form.photo.data
            if file:
                filename = photos.save(file)
                recipe.photo = '/static/uploads/' + filename
            db_sess.commit()
            return redirect(url_for('read_recipe', id=id))

    return render_template('create_recipes.html', form=form, title="Редактирование рецепта")


@app.route('/recipe_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def recipe_delete(id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipes).filter(Recipes.id == id).first()
    db_sess.delete(recipe)
    db_sess.query(Comments).filter(Comments.recipe_id == 3).delete()

    for user in db_sess.query(User).all():
        try:
            liked_recipes = user.liked_recipes.split(',')
            liked_recipes.remove(str(id))
            liked_recipes = [r for r in liked_recipes if r != '']
            user.liked_recipes = ','.join(liked_recipes) + ','
        except: pass

    db_sess.commit()
    return redirect(url_for('my_recipes'))


@app.route('/delete_profile', methods=['GET', 'POST'])
@login_required
def delete_profile():
    db_sess = db_session.create_session()
    id = current_user.id
    list_recipes_user = [str(recipe.id) for recipe in db_sess.query(Recipes).filter(Recipes.user_id == id)]

    for recipe in db_sess.query(Recipes).all():
        try:
            recipe.count_likes = int(recipe.count_likes) - 1
            users_likes = recipe.users_likes.split(',')
            users_likes.remove(str(id))
            users_likes = [r for r in users_likes if r != '']
            recipe.users_likes = ','.join(users_likes) + ','
        except: pass

    for user in db_sess.query(User).all():
        try:
            need_recipes = [recipe for recipe in user.liked_recipes.split(',') if recipe not in list_recipes_user]
            user.liked_recipes = ','.join(need_recipes)
        except: pass

    db_sess.query(Comments).filter(Comments.user_id == id).delete()
    db_sess.query(Recipes).filter(Recipes.user_id == id).delete()
    user = db_sess.query(User).filter(User.id == id).first()
    db_sess.delete(user)
    db_sess.commit()
    return redirect('/')


@app.route('/restaurants', methods=['GET', 'POST'])
def restaurant():
    if request.method == 'POST':
        city = request.form['search_req']
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={city}&format=json"
        response = requests.get(geocoder_request)

        if not response:
            return render_template("restaurants.html", msg='Не понял.')

        json_response = response.json()
        try:
            address_ll = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']

            search_api_server = "https://search-maps.yandex.ru/v1/"
            address_ll = ",".join(address_ll.split())
            search_params = {
                "apikey": 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
                "text": "ресторан кафе",
                "lang": "ru_RU",
                "ll": address_ll,
                "type": "biz"
            }

            response = requests.get(search_api_server, params=search_params)

            json_response = response.json()
            restaurants = json_response['features']
            restaurants_list = list()
            for restaurant in restaurants:
                data = {}
                data['name'], data['address'], data['phone'], data['url'], data[
                    'hours'], data['photo'] = None, None, None, None, None,\
                    'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1a/a3/f2/09/caption.jpg?w=600&h=-1&s=1'
                try:
                    data['name'] = restaurant['properties']['CompanyMetaData']['name']
                    data['address'] = restaurant['properties']['CompanyMetaData']['address']
                    data['phone'] = restaurant['properties']['CompanyMetaData']['Phones'][0]['formatted']
                    data['url'] = restaurant['properties']['CompanyMetaData']['url']
                    data['hours'] = restaurant['properties']['CompanyMetaData']['Hours']['text'].split(';')
                except:
                    pass
                restaurants_list.append(data)

            return render_template('restaurants.html', data=restaurants_list)
        except:
            return render_template("restaurants.html", msg='Не понял.')

    return render_template('restaurants.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile_user():
    form = EditForm()
    db_sess = db_session.create_session()
    if request.method == 'GET':
        form.name_edit.data = current_user.name
        form.surname_edit.data = current_user.surname
        form.email_edit.data = current_user.email
    if request.method == 'POST':
        user = db_sess.query(User).filter(User.id == current_user.id).first()

        if form.email_edit.data != user.email and form.email_edit.data in [user.email for user in db_sess.query(User)]:
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
    return render_template('profile_user.html', authenticated=True, user=current_user)


@app.route('/home')
@login_required
def home_user():
    return render_template('home.html', home=True)


@app.errorhandler(404)
def page_not_fount(error):
    res = make_response(f'Страница не найдена, но мы её найдем')
    return res


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
