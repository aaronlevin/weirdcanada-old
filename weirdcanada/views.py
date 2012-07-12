# coding=utf-8 

import datetime
import hashlib
import S3
import sys

from flask import current_app
from flask import flash
from flask import Flask
from flask import g
from flask import redirect
from flask import render_template
from flask import Response
from flask import request
from flask import session
from flask import url_for
from flaskext.principal import AnonymousIdentity
from flaskext.principal import Identity
from flaskext.principal import identity_changed
from flaskext.principal import identity_loaded
from flaskext.principal import Permission
from flaskext.principal import Principal
from flaskext.principal import RoleNeed
from forms import LoginForm, PostForm
from helpers import slug
from models import User
from models import Post
from models import WCConfig
from weirdcanada import app

# CSRF Token
app.secret_key = WCConfig.config['app']['secret_key']

# File Upload Settings
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','mp3','ogg','gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask-Principal Identity & Authorzation mngmt
principals = Principal(app)
admin_permission = Permission(RoleNeed('admin'))

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    user = User().collection.find_one({'username':identity.name})
    if user:
        session['psh'] = hashlib.sha1(identity.name).hexdigest()
        for role in user['roles']:
            identity.provides.add(RoleNeed(role))

# Placing Today's date in the global context for use in Jinja
@app.context_processor
def todays_date():
    today = datetime.date.today()
    return dict(todays_date=today.strftime('%Y-%m-%d'))

# Place hashed username in 'wcmsg' cookie to be used for message pushing
@app.after_request
def after_request(response):
    if session.has_key('psh'):
        response.set_cookie('wcmsg', value=session['psh'])
    else:
        response.set_cookie('wcmsg',value='Stop looking at our cookies')
    return response

# ******* FINALLY, THE VIEWS ********

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        if User().check_username_password_combo(username=form.data['username'], password=form.data['password']):
            identity_changed.send(app,identity=Identity(form.data['username']))
            flash('Congrats! You\'ve succesfully logged in!')
            return redirect(url_for('index'))
        else:
            flash('Incorrect Username and/or Password, bro.')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    del session['psh']
    flash('You\'ve sucesfully logged out, dude! Please come back!')
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@admin_permission.require()
def admin():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.insert_from_form(form=form)
        
        # Route to index
        return redirect(url_for('index'))
    else:
        flash(str(form.errors))
        return render_template('admin.html', form=form)

@app.route('/new-canadiana/<string:object_id>', methods=['GET','POST'])
def new_canadiana(object_id):
    post = Post()
    tmp = post.collection.find_one({'_id':object_id})
    flash(tmp)
    return redirect(url_for('index'))

@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')
