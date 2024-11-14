import RPi.GPIO as GPIO
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functools import wraps
import os



app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
# pins = {
#    23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
#    24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
#    }

# # Set each pin as an output and make it low:
# for pin in pins:
#    GPIO.setup(pin, GPIO.OUT)
#    GPIO.output(pin, GPIO.LOW)

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


# Set each pin as an output and make it low:
# Function to initialize GPIO pins
def init_gpio():
    # Set the GPIO mode (BCM or BOARD)
    GPIO.setmode(GPIO.BCM)  # Use GPIO.BOARD if you want to use physical pin numbering
    
    # Query all pins from the database
    pins = Pins.query.all()

    # Set up each pin from the database as an output and set it to LOW
    for pin in pins:
        print(pin.gpio)
        GPIO.setup(int(pin.gpio), GPIO.OUT)
        GPIO.output(int(pin.gpio), GPIO.LOW)

# This function will run once when the app starts
@app.before_first_request
def setup_gpio():
    init_gpio()  # Initialize GPIO pins before handling any requests



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
    
def check_admin(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != 'admin':
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def create_log(pin, status):
    gpio = Pins.query.filter_by(gpio=pin).first()
    
    record = Logs(pin_number = pin,
                pin_name = gpio.name,
                name = session['name'],
                username = session['username'],
                role = session['role'], 
                action=status)
    db.session.add(record)
    db.session.commit()
    
    

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
        print(user.password)
        # Check if the user exists and the password matches
        if not user or not check_password_hash(user.password, password):
            flash("Invalid username and/or password", "error")
            return render_template("auth/login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
        session["name"] = user.name
        session["username"] = user.username
        session["role"] = user.role
        
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
    pin_status ={}
    for pin in pins:
        GPIO.setup(pin.gpio, GPIO.OUT)
        gpio_pin = pin.gpio
        pin_state = GPIO.input(gpio_pin)
        print(pin_state)
        # Check if the pin is HIGH or LOW
        if pin_state == GPIO.HIGH:
            pin_status[gpio_pin] = 'on'
        else:
            pin_status[gpio_pin] = 'off'
    
    logs = Logs.query.order_by(Logs.id.desc()).limit(5).all()

    return render_template('index.html', pins=pins, pin_status=pin_status, logs=logs)
    
@app.route('/users')
@login_required
@check_admin
def users():
    users = Users.query.all()
    return render_template('users/users.html', users=users)

@app.route('/add-user', methods=['GET', 'POST'])
@login_required
@check_admin
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
      
        
@app.route('/del-user', methods=['POST'])
@check_admin
@login_required
def del_user():
    if request.method == "POST":
        id = request.form.get('del_id')
        
        record = Users.query.get(id)
        if record and record.username != 'admin':
        # Check if the record exists
            db.session.delete(record)
            db.session.commit()
        
    return redirect('/users')


@app.route('/pins')
@login_required
@check_admin
def pins():
    pins = Pins.query.all()
    return render_template('pins/pins.html', pins=pins)

@app.route('/add-pin', methods=['GET', 'POST'])
@login_required
@check_admin
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
        
@app.route('/del-pin', methods=['POST'])
@check_admin
@login_required
def del_pin():
    if request.method == "POST":
        id = request.form.get('del_id')
        
        record = Pins.query.get(id)
        # Check if the record exists
        if record:
            db.session.delete(record)
            db.session.commit()
        
    return redirect('/pins')
   

@app.route('/logs')
@login_required
def logs():
    logs = Logs.query.order_by(Logs.id.desc()).all()
    pins = Pins.query.all()
    return render_template('logs/logs.html', logs=logs, pins=pins)
    



@app.route("/relay/<pin>/<status>")
@login_required
def relay(pin, status):
    pin = int(pin)
    if status == 'on':
        GPIO.output(pin, GPIO.HIGH)
        print('Relay 1 ON')
    elif status == 'off':
        GPIO.output(pin, GPIO.LOW)
        print('Relay 1 OFF')
    
    # CREATE LOG
    create_log(pin, status)
    
    return redirect("/")


@app.route('/welcome/<name>')
def welcome(name):
    return f"Hi {name}"
    
    




if __name__ == '__main__':

    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8080)
