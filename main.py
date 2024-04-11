from flask import Flask, render_template, redirect, make_response, url_for, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.recipes import Recipes
from forms.login import LoginForm
from forms.regist import RegisterForm
from forms.recipe import RecipeForm


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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
            return redirect(url_for('home_user'))
        return render_template('login.html', form=form, message='Неверная почта или пароль')
    return render_template('login.html', form=form)


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        if form.email.data in [user.email for user in db_sess.query(User)]:
            form.email.data = ""
            return render_template('register.html', form=form, message='Такой пользователь уже существует')

        elif form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message='Пароли не совпадают')

        else:
            user = User(name=form.name.data, surname=form.surname.data, email=form.email.data)
            db_sess.add(user)
            user.set_password(form.password.data)
            db_sess.commit()
            login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home_user'))
    return render_template('register.html', form=form)




@app.route('/recipes')
def all_recipes():
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipes).filter(Recipes.is_private != True)
    return render_template('recipes.html', recipes=recipes)


@app.route('/my_recipes')
def my_recipes():
    return render_template('recipes.html', recipes=current_user.recipes, add_recipes=True)


@app.route('/read_recipe', methods=['POST'])
def read_recipe():
    db_sess = db_session.create_session()
    recipe_id = request.form['recipe']
    recipe = db_sess.query(Recipes).filter(Recipes.id == recipe_id).first()
    return render_template('read_recipe.html', recipe=recipe)


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
        recipe.photo = form.photo.data

        if recipe.name == '':
            message = 'Укажите название рецепта'
        elif recipe.time == '':
            message = 'Укажите время приготовления'
        elif recipe.text == '':
            message = 'Укажите рецепт'

        if recipe.name == '' or recipe.text == '' or recipe.time == '':
            return render_template('create_recipes.html', form=form, message=message)

        recipe.is_private = form.is_private.data
        current_user.recipes.append(recipe)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('recipes')
    return render_template('create_recipes.html', form=form)



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
    # db_sess = db_session.create_session()


    app.run(port=8080, host='127.0.0.1', debug=True)



if __name__ == '__main__':
    main()
