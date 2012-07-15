# coding=utf-8 

import datetime
import S3
import sys

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask.ext.principal import AnonymousIdentity
from flask.ext.principal import Identity
from flask.ext.principal import identity_changed
from flask.ext.principal import identity_loaded
from flask.ext.principal import Permission
from flask.ext.principal import RoleNeed
from forms import LoginForm, PostForm
from models import User
from models import Post
from weirdcanada import app

# Permissions

admin_permission = Permission(RoleNeed('admin'))

# Views

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
#@admin_permission.require()
def admin():
    form = PostForm()
    print form
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
