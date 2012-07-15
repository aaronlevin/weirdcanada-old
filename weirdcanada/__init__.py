import datetime
import hashlib
from flask import Flask
from flask import session
from flask.ext.principal import identity_loaded
from flask.ext.principal import Principal
from flask.ext.principal import RoleNeed
from models import User
from models import WCConfig

app = Flask(__name__)

# CSRF Token
app.secret_key = WCConfig.config['app']['secret_key']

# File Upload Settings
UPLOAD_FOLDER = ''
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','mp3','ogg','gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask-Principal Identity & Authorzation mngmt
principals = Principal(app)

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
    if 'psh' in session:
        response.set_cookie('wcmsg', value=session['psh'])
    else:
        response.set_cookie('wcmsg',value='Stop looking at our cookies')
    return response

import weirdcanada.views
import weirdcanada.ajax


