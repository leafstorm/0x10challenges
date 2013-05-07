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
from flask.ext.wtf import Form
from wtforms.fields import TextField
from wtforms.validators import DataRequired, Optional, Length

accounts = Blueprint('accounts', __name__)

class NicknameForm(Form):
    nickname =  TextField(u"New Nickname", validators=[DataRequired(),
                                                       Length(5, 32)])


@accounts.route('/set-nick', methods=['GET', 'POST'])
def set_nick():
    if 'nickname' in session:
        form = NicknameForm(nickname=session['nickname'])
    else:
        form = NicknameForm()

    if form.validate_on_submit():
        session['nickname'] = form.nickname.data

    return render_template("accounts/set-nick.html", form=form)
