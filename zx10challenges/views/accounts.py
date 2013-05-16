# -*- coding: utf-8 -*-
"""
zx10challenges.views.accounts
=============================
This handles user accounts and stuff.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
import os
from flask import Blueprint, abort, request, render_template, session
from flask.ext.login import (current_user, login_user, logout_user,
                             login_required)
from flask.ext.wtf import Form
from wtforms.fields import TextField
from wtforms.validators import DataRequired, Optional, Length
from ..login import verify_assertion
from ..models import User

accounts = Blueprint('accounts', __name__)

@accounts.route('/persona-login', methods=['POST'])
def persona_login():
    email, status = verify_assertion(request.form['assertion'],
                                     request.url_root)
    if email is not None and current_user.email != email:
        user = User.get_or_create(email)
        login_user(user)
        return "OK"
    else:
        abort(403)


@accounts.route('/persona-logout', methods=['POST'])
def persona_logout():
    logout_user()
    return "OK"


class NicknameForm(Form):
    nickname =  TextField(u"New Nickname", validators=[DataRequired(),
                                                       Length(5, 32)])


@accounts.route('/set-nick', methods=['GET', 'POST'])
@login_required
def set_nick():
    form = NicknameForm(nickname=current_user.nickname)

    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.store()

    return render_template("accounts/set-nick.html", form=form)

