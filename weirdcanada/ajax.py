"""
This module contains code to hangle ajax requests. The service is built around
the following infrastructure:
    - messages are held within a variable in app.config called 'polling_message'
    - polling_message has the following form:
        { updated: True/False, payload: message }
"""
from copy import copy
from flask import jsonify
from flask import flash
from flask import session
from weirdcanada import app
from models import PushMessage
from werkzeug.contrib.securecookie import SecureCookie
import random

@app.route('/ajax/push', methods=['GET'])
def push():
    p = PushMessage()
    if session.has_key('psh'):
        p.trigger('message',{'payload':'Random: '+ str(random.randint(1,100000)) })
    else:
        p.trigger('message',{'payload':'user not in session '})
    return jsonify({})
