from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import desc
from werkzeug.urls import url_parse
from extensions import db, login_manager, bootstrap
from models import User, Expense
from forms import ExpenseForm, LoginForm, RegistrationForm
import os

#  mysql database configuration
MYSQL_HOST = 'localhost'
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = ''
MYSQL_DATABASE_NAME = ''
MYSQL_PORT = '3306'



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bootstrap.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        flash("You are now signed in!", "success")
        return redirect(next_page)
    return render_template('form.html', title='Login', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data, 
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return(redirect(url_for('login')))
    return render_template('form.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You've signed out!", "success")
    return redirect(url_for('login'))


@app.route("/dashboard")
@login_required
def home():
    all_expenses = Expense.query.order_by(desc(Expense.date)).filter_by(user_id=current_user.id).all()
    return render_template("home.html", expenses=all_expenses)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(title=form.title.data, 
                          category=form.category.data, 
                            amount=form.amount.data, 
                            date=form.date.data,
                            user_id=current_user.id)
                                                
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('home'))

    form.date.data = datetime.utcnow()
    return render_template("form.html", form=form,title="Add new expense")


@app.route("/update/<int:expense_id>", methods=['GET', 'POST'])
@login_required
def update(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    form = ExpenseForm()
    if form.validate_on_submit():
        expense.title = form.title.data
        expense.category = form.category.data
        expense.amount = form.amount.data
        expense.date = form.date.data
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = expense.title
        form.category.data = expense.category
        form.amount.data = expense.amount
        form.date.data = expense.date
    return render_template('form.html', form=form, title='Edit Expense')

@app.route("/delete/<int:expense_id>", methods=['POST'])
@login_required
def delete(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
