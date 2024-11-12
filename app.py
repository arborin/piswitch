from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functools import wraps
import os



app = Flask(__name__)

app.secret_key =  "RANDOM STRING"#os.urandom(24)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db = SQLAlchemy(app)


class Pins(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    gpio = db.Column(db.Integer)
    name = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    
    def __repr__(self):
        return f"GPIO: {self.gpio}, NAME: {self.name}"
        
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255))
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    role = db.Column(db.String(20))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    
    def __repr__(self):
        return f"Username: {self.username}, NAME: {self.name}, ROLE: {self.role}"       

class Logs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    pin_number = db.Column(db.String(255))
    pin_name = db.Column(db.String(255))
    name = db.Column(db.String(255))
    username = db.Column(db.String(20))
    role = db.Column(db.String(20))
    action = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
        
    def __repr__(self):
        return f"Pin Number: {self.pin_number}, Pin Name: {self.pin_name}, Action: {self.action}"     


def login_required(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        # Query database for username

        user = Users.query.filter_by(username=username).first()
        print(user)
        # Check if the user exists and the password matches
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username and/or password", "error")
            return render_template("auth/login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
        session["name"] = user.name
        session["username"] = user.username
        
        # Redirect user to the home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("auth/login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/')
@login_required
def index():
    pins = Pins.query.all()
    pin_status = {23: 'on', 24: 'on'}    
    return render_template('index.html', pins=pins, pin_status=pin_status)
    
@app.route('/users')
@login_required
def users():
    users = Users.query.all()
    return render_template('users/users.html', users=users)

@app.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == "POST":
        username = request.form.get('username')
        name = request.form.get('name')
        password = generate_password_hash(request.form.get('password'))
        role = request.form.get('role')
        status = request.form.get('status')
        
        user = Users(username=username, name=name, password=password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        
        return redirect('/users')
    elif request.method == "GET":
        return render_template('users/add_user.html')

@app.route('/pins')
@login_required
def pins():
    pins = Pins.query.all()
    return render_template('pins/pins.html', pins=pins)

@app.route('/add-pin', methods=['GET', 'POST'])
@login_required
def add_pin():
    if request.method == "POST":
        name = request.form.get('name')
        gpio = request.form.get('gpio')
        
        pin = Pins(gpio=gpio, name=name)
        db.session.add(pin)
        db.session.commit()
        
        return redirect('/pins')
    elif request.method == "GET":
        return render_template('pins/add_pin.html')

@app.route('/logs')
@login_required
def logs():
    return render_template('logs/logs.html')
    

@app.route('/relay/<pin>/<status>')
@login_required
def relay(pin, status):
    print("-------------------------------")
    print(pin)
    print(status)
    print("-------------------------------")
    return redirect('/')


@app.route('/welcome/<name>')
def welcome(name):
    return f"Hi {name}"
    
    




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)