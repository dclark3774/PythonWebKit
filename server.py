# Import dependencies
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required
import logging
import pxc_modules.plcnextAPI as API
import socket
import json


# Get the local IP address of the PLCnext
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# Initial setup of flask server
app = Flask(__name__, static_folder='public', template_folder='views')
app.config['SECRET_KEY'] = 'Secret!'
# loginManager = LoginManager()
# loginManager.init_app(app)

# Setting IP address, WBM address, and eHMI address for redirects.
ip = get_ip()
wbm = 'https://'+ip+'/wbm'
ehmi = 'https://'+ip+'/ehmi'


#@loginManager.user_loader
#def load_user(user_id):
#    with open('config/user.json') as file:
#        users = json.load(file)
#    return users[user_id]


@app.route('/')
def goToPage():
    #if loginManager.unauthorized():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            message = 'Invalid Credentials. Please Try Again.'
        else:
            return redirect(url_for('dashboard'))
    return render_template('login.html', message=message, ip=ip, wbm=wbm, ehmi=ehmi)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/change-pass')
def changePass():
    return render_template('change-pass.html', message='')


@app.route('/logout')
def logout():
    return render_template('login.html', message='')


@socketio.on('connect')
def connection():
    emit('welcomeMessage', 'Welcome to the Phoenix Contact Node Web Kit for PLCnext!')


if __name__ == '__main__':
    socketio.run(app, host=ip, port=5000, debug=True)
    plcnextAPI = API.getData(waitTime=1)
