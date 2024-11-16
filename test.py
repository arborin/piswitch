
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)




@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/relay/<action>")
def action(action):
    print(action)
    if int(action) == 1:
        print("HIII")
        GPIO.output(23, GPIO.HIGH)
        print('Relay 1 ON')
    elif int(action) == 0:
        GPIO.output(23, GPIO.LOW)
        print('Relay 1 OFF')
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0')