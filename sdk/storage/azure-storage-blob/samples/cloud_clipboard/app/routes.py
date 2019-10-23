from flask import render_template

from app import app

from app.models import User

@app.route('/')
@app.route('/index')
def index():
    u = User()
    return render_template('index.html', title="Home", user=u)