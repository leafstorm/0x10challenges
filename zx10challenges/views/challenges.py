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
from flask import Blueprint, abort, request, render_template, flash, session
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional
from ..challenges import CHALLENGES
from ..models import Submission, StopEvaluating

challenges = Blueprint('challenges', __name__)

@challenges.route('/')
def index():
    return render_template("index.html", challenges=CHALLENGES.values())


class AttemptForm(Form):
    assembly =  TextAreaField(u"Assembly Code", validators=[DataRequired()])
    notes =     TextAreaField(u"Notes", validators=[Optional()])
    publish =   BooleanField(u"Publish Code", validators=[Optional()])


@challenges.route('/challenge/<id>/', methods=['GET', 'POST'])
def attempt(id):
    if id not in CHALLENGES:
        abort(404)
    challenge = CHALLENGES[id]

    form = AttemptForm()
    if form.validate_on_submit():
        sub = challenge.create_submission()
        sub.assembly = form.assembly.data
        sub.notes = form.notes.data

        try:
            challenge.evaluate(sub)
        except StopEvaluating:
            pass

        can_submit = 'nickname' in session and sub.passed

        if can_submit and request.form.get('action') == 'submit':
            sub.user_nickname = session['nickname']
            sub.published = form.publish.data
            sub.submit()
            sub.store()
            flash(u"Your code has been submitted! Once it's approved, it "
                   "will show up in the leaderboard.", 'success')
    else:
        sub = None
        can_submit = False

    return render_template("attempt.html", challenge=challenge, form=form,
                           submission=sub, can_submit=can_submit)


@challenges.route('/challenge/<id>/leaderboard')
def leaderboard(id):
    if id not in CHALLENGES:
        abort(404)
    challenge = CHALLENGES[id]

    boards = challenge.get_leaderboards()

    return render_template("leaderboard.html", challenge=challenge,
                           boards=boards)
