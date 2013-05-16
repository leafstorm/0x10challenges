# -*- coding: utf-8 -*-
"""
zx10challenges.login
====================
This contains the login infrastructure -- the Flask-Login manager, and the
Persona interface code.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
import requests
from flask.ext.login import LoginManager, AnonymousUser
from .models import User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
    return User.load(userid)


class ZXAnonymousUser(AnonymousUser):
    email = None
    nickname = None
    join_date = None

    is_admin = False
    is_disabled = True
    is_muted = False


login_manager.anonymous_user = ZXAnonymousUser


def verify_assertion(assertion, audience):
    payload = {'assertion': assertion, 'audience': audience}
    response = requests.post('https://verifier.login.persona.org/verify',
                             data=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get('status', 'failure') == 'okay':
            return data['email'], None
        else:
            return None, data['reason']
    else:
        return None, u"Verifier returned a %d error." % response.status_code

