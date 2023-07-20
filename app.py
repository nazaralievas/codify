from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'QWERTY12345'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Здесь устанавливается атрибут login_view объекта login_manager на значение 'login'.
# Это указывает LoginManager на представление Flask, которое будет использоваться для отображения страницы входа в систему,
# если пользователь не аутентифицирован и попытается получить доступ к защищенным страницам.

db = SQLAlchemy(app)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    mentor = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    course = db.relationship('Course', backref='orders', cascade='all')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Юзернейм"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Пароль"})
    submit = SubmitField("Зарегистрироваться")
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError("Этот юзернейм занят, выберите другой")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Юзернейм"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Пароль"})
    submit = SubmitField("Войти")


with app.app_context():
    db.create_all()


@app.route('/')
def homepage():
    courses = Course.query.all()
    return render_template('homepage.html', courses=courses)


@app.route('/course/<int:id>')
def course(id):
    course = Course.query.get_or_404(id)
    return render_template('course.html', course=course)


@app.route('/add', methods=["POST", "GET"])
@login_required
def add():
    if request.method == "POST":
        title = request.form['title']
        mentor = request.form['mentor']
        description = request.form['description']
        article = Course(title=title, mentor=mentor, description=description)
        db.session.add(article)
        db.session.commit()
        return redirect('/')
    return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect('/')


@app.route('/update/<int:id>', methods=["POST", "GET"])
def update(id):
    course = Course.query.get_or_404(id)
    if request.method == "POST":
       course.title = request.form['title']
       course.mentor = request.form['mentor']
       course.description = request.form['description']
       db.session.commit()
       return redirect('/')
    return render_template('update.html', course=course)


@app.route('/order/<int:id>', methods=["POST", "GET"])
def order(id):
    course = Course.query.get_or_404(id)
    if request.method == "POST":
        full_name = request.form['full_name'].title()
        phone = request.form['phone']
        email = request.form['email']
        order = Order(course_id=id, course=course, full_name=full_name, phone=phone, email=email)
        db.session.add(order)
        db.session.commit()
        return redirect(f'/course/{id}')
    return render_template('order.html', course=course)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user.password == form.password.data:
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True)
