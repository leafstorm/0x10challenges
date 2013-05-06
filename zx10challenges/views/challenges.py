# -*- coding: utf-8 -*-
"""
zx10challenges.views.challenges
===============================
This contains the bulk of the app's code, as it deals with accepting user
submissions and testing them.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
import os
from flask import Blueprint, abort, request, render_template
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField
from wtforms.validators import DataRequired, Optional
from ..challenges import CHALLENGES
from ..challenges.base import StopEvaluating
from ..models import Submission

challenges = Blueprint('challenges', __name__)

@challenges.route('/')
def index():
    return render_template("index.html", challenges=CHALLENGES.values())


class AttemptForm(Form):
    assembly =  TextAreaField(u"Assembly Code", validators=[DataRequired()])
    notes =     TextAreaField(u"Notes", validators=[Optional()])


@challenges.route('/challenge/<id>/', methods=['GET', 'POST'])
def attempt(id):
    if id not in CHALLENGES:
        abort(404)
    challenge = CHALLENGES[id]

    form = AttemptForm()
    if form.validate_on_submit():
        sub = Submission(challenge_id=id, assembly=form.assembly.data,
                         notes=form.notes.data)
        try:
            challenge.evaluate(sub)
        except StopEvaluating:
            pass
    else:
        sub = None

    return render_template("attempt.html", challenge=challenge, form=form,
                           submission=sub)
