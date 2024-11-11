from flask import Flask, render_template, url_for


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/add-user')
def add_user():
    return render_template('add_user.html')

@app.route('/pins')
def pins():
    return render_template('pins.html')

@app.route('/add-pin')
def add_pin():
    return render_template('add_pin.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')
    



    
@app.route('/welcome/<name>')
def welcome(name):
    return f"Hi {name}"
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)