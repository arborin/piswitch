import RPi.GPIO as GPIO
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functools import wraps
import os



app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

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
        
        if not user or user.status == 'disable':
            flash("User not activated!", "danger")
            return render_template("auth/login.html")
        
        # Check if the user exists and the password matches
        if not check_password_hash(user.password, password):
            flash("Invalid username and/or password", "danger")
            return render_template("auth/login.html")

        # Remember which user has logged in
        session["user_id"] = user.id
        session["name"] = user.name
        session["role"] = user.role
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = 'user'
        status = 'disable'
        
        if password != '' and confirm_password != '' and password == confirm_password:
            password = generate_password_hash(password)
        else:
            flash('Check your password!', 'danger')
            return redirect('/login')
        
        
        # CHECK FIRST USER
        users = Users.query.all()
        if not users:
            role = 'admin'
            status = 'active'
        
        user = Users(username=username, name=name, password=password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        flash('User Created!', 'success')
        return redirect('/login')

    if request.method == 'GET':
        return render_template('auth/register.html')
        


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
    print(">>>>> ", len(logs))
    return render_template('index.html', pins=pins, pin_status=pin_status, logs=logs, log_len=int(len(logs)))
    
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
        id = request.form.get('id')
        username = request.form.get('username').strip()
        name = request.form.get('name').strip()
        password = request.form.get('password').strip()
        role = request.form.get('role')
        status = request.form.get('status')
        
        if id:
            user = Users.query.filter_by(id=id).first()
            user.username = username
            user.name = name 
            user.role = role
            user.status = status
            if password != '':
                user.password = generate_password_hash(password)
            
        else:
            if password != '':
                flash("Password is empty!", "danger")
                return redirect('/users')
            else:
                user = Users(username=username, name=name, password=password, role=role, status=status)
                db.session.add(user)
        
        db.session.commit()
        flash("Operation successfully done", "success")
        return redirect('/users')
    elif request.method == "GET":
        return render_template('users/add_user.html')


@app.route('/edit-user/<id>')
@login_required
@check_admin
def edit_user(id):
    user = Users.query.filter_by(id=id).first()
    
    return render_template('users/edit_user.html', user=user)
    
        
@app.route('/del-user', methods=['POST'])
@check_admin
@login_required
def del_user():
    if request.method == "POST":
        id = request.form.get('del_id')
        record = Users.query.get(id)
        
        print(id, session['user_id'])
        
        
        if int(id) == int(session['user_id']):
            # Can not delete your user
            flash("You can not delete your user", "danger")   
            return redirect('/users')
            
        elif record:
        # Check if the record exists
            db.session.delete(record)
            db.session.commit()
            flash("Operation successfully done", "success")
        
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
        id = request.form.get('id')
        
        if id:
            pin = Pins.query.filter_by(id=id).first()
            pin.gpio = gpio
            pin.name = name
        else:
            pin = Pins(gpio=gpio, name=name)
            db.session.add(pin)
        
        db.session.commit()
        flash("Operation successfully done", "success")
        return redirect('/pins')
    elif request.method == "GET":
        return render_template('pins/add_pin.html')
        
@app.route('/edit-pin/<id>')
@login_required
@check_admin
def edit_pin(id):
    pin = Pins.query.filter_by(id=id).first()
    
    return render_template('pins/edit_pin.html', pin=pin)
    
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
    
        flash("Operation successfully done", "success")    
    return redirect('/pins')
   

@app.route('/logs')
@login_required
def logs():
    filter = {}
    page = request.args.get('page', 1, type=int)  # Get current page from request, default is 1
    per_page = 15  # Number of items per page

    date_from = request.args.get('date_from')
    filter['date_from'] = date_from
    date_to = request.args.get('date_to')
    filter['date_to'] = date_to
    gpio = request.args.get('gpio')
        
    logs = Logs.query
   
    if gpio:
        filter['gpio'] = int(gpio)
        logs = logs.filter_by(pin_number=gpio)
        
    if date_from and date_from != 'None':
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        logs = logs.filter(func.date(Logs.created_at) >= date_from)
    
    if date_to and date_to != 'None':
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        logs = logs.filter(func.date(Logs.created_at) <= date_to)
        
    
    logs = logs.order_by(Logs.id.desc()).paginate(page=page, per_page=per_page)
    
    pins = Pins.query.all()
    return render_template('logs/logs.html', logs=logs, pins=pins, filter=filter)
    



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


@app.route('/profile')
@login_required
def profile():    
    return render_template('profile/profile.html')
    

@app.route('/update-profile', methods=['post'])
@login_required
def update_profile():
    id = session['user_id']
    user = Users.query.filter_by(id=id).first()
    
    name = request.form.get('name')
    password = request.form.get('password')
        
    if password:
        password = generate_password_hash(password)
        user.password = password
    
    if name:
       user.name = name
       session['name'] = name
              
    db.session.commit()
        
    return redirect('/')

    

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8080)
