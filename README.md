# Pi Switch
#### Video Demo:  https://www.youtube.com/watch?v=vr2X-V9a4fY
#### Description:
PiSwitch: a web-based flask application running on a Raspberry Pi that allows you to control high-voltage devices remotely. With user management, action and logging.


#### Setup:
Download and install requirements

```
pip install -r requirements.txt
```

run:
```
python
```

and create database:
```
from app import app
from app import db


with app.app_context():
    db.create_all()
```    
    
run application:

```
python app.py
```

go to web browser: 

http://localhost:8080

and register user. first user has admin role and active status.

(if you will register nect user you have to enable his status from admin user.)

connect raspberry gpio pins to your relay and add them in application.

now you can make actions from web interface.

