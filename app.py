from flask import (Flask, g, render_template, flash, redirect, url_for,
                    abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                            login_required, current_user)

import forms
import models

app = Flask(__name__)
app.secret_key = 'jalhf.fskrgj.sr;grrlghs.saji;rs/srg/srgjrski;rji4439u4fj/e;wf490jgie'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close database connection after each response."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('You are now a Taco Cat member!', 'success')
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password does not match.", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Welcome {}! You are now logged in.'.format(user.email.split('@')[0]), 'success')
                return redirect(url_for('index'))
            else:
                flash("Your email or password does not match.", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('index'))


@app.route('/new_taco', methods=('GET', 'POST'))
@login_required
def taco():
    form = forms.TacoForm()
    if form.validate_on_submit():
        models.Taco.create(
            user=g.user._get_current_object(),
            protein=form.protein.data,
            shell=form.shell.data,
            cheese=form.cheese.data,
            extras=form.extras.data.strip()
        )
        flash('Taco created!', 'success')
        return redirect(url_for('index'))
    return render_template('taco.html', form=form)


@app.route('/profile/<email>')
def profile(email):
    user = models.User.get(models.User.email**email)
    tacos = user.tacos.select().limit(100)
    if tacos.count() == 0:
        return redirect(url_for('index'))
    return render_template('profile.html', tacos=tacos, user=user)


@app.route('/delete/<int:taco_id>')
def delete(taco_id):
    try:
        email = g.user._get_current_object().email
        models.Taco.select().where(models.Taco.id == taco_id).get().delete_instance()
        flash('Deleted Taco!', 'success')
    except models.DoesNotExist:
        abort(404)
    return redirect(url_for('profile', email=email))



@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/')
def index():
    tacos = models.Taco.select().limit(100)
    return render_template('index.html', tacos=tacos)


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            email='ronaldw@gmail.com',
            password='password'
        )
    except ValueError:
        pass
    app.run()
