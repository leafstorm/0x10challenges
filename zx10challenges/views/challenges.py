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
from flask import (Blueprint, abort, request, render_template, flash, session,
                   redirect, url_for)
from flask.ext.login import current_user, login_required
from flask.ext.wtf import Form
from wtforms.fields import TextAreaField, BooleanField, RadioField
from wtforms.validators import DataRequired, Optional
from ..challenges import CHALLENGES
from ..models import Submission, StopEvaluating

challenges = Blueprint('challenges', __name__)

@challenges.route('/')
def index():
    return render_template("challenges/index.html",
                           challenges=CHALLENGES.values())


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

        can_submit = current_user.is_authenticated()

        if can_submit and request.form.get('action') == 'submit':
            sub.user = current_user
            sub.published = form.publish.data
            sub.submit()
            sub.store()
            flash(u"Your code has been submitted! Once it's approved, it "
                   "will show up in the leaderboard.", 'success')
    else:
        sub = None
        can_submit = False

    return render_template("challenges/attempt.html",
                           challenge=challenge, form=form,
                           submission=sub, can_submit=can_submit)


@challenges.route('/challenge/<id>/leaderboard')
def leaderboard(id):
    if id not in CHALLENGES:
        abort(404)
    challenge = CHALLENGES[id]

    boards = challenge.get_leaderboards()

    return render_template("challenges/leaderboard.html",
                           challenge=challenge, boards=boards)


@challenges.route('/my-submissions')
@login_required
def my_submissions():
    submissions = current_user.get_submissions()

    return render_template("challenges/my-submissions.html",
                           submissions=submissions)


@challenges.route('/submission/<id>')
def submission(id):
    sub = Submission.load(id)
    if sub is None:
        abort(404)

    challenge = CHALLENGES.get(sub.challenge_id)
    if challenge is None:
        abort(400)

    # If it's not approved and published, then only the submitter
    # and the administrator can view it.
    if not (current_user.id == sub.user_id or current_user.is_admin):
        if not sub.approved:
            # From this user's point of view, the submission doesn't exist.
            abort(404)
        elif not sub.published:
            flash(u"This submission's author has elected not to publish "
                   "their code.", 'error')
            return redirect(url_for('challenges.leaderboard',
                                    id=challenge.id))

    return render_template("challenges/submission.html",
                           challenge=challenge, submission=sub)


@challenges.route('/review-queue/')
@login_required
def review_queue():
    if not current_user.is_admin:
        abort(403)
    submissions = Submission.get_review_queue()

    return render_template("challenges/review-queue.html",
                           submissions=submissions)


DECISIONS = [
    (u'approve',  u"Approve"),
    (u'reject',   u"Reject"),
    (u'mute',     u"Reject and Mute")
]

class ReviewForm(Form):
    admin_notes = TextAreaField(u"Notes", validators=[Optional()])
    decision    = RadioField(u"Decision", choices=DECISIONS,
                             validators=[DataRequired()])


@challenges.route('/review-queue/<id>', methods=['GET', 'POST'])
@login_required
def review_submission(id):
    if not current_user.is_admin:
        abort(403)

    sub = Submission.load(id)
    if sub is None:
        abort(404)

    challenge = CHALLENGES.get(sub.challenge_id)
    if challenge is None:
        abort(400)

    if not sub.needs_review:
        flash(u"This submission has already been reviewed.", 'error')
        return redirect(url_for('challenges.review_queue'))

    form = ReviewForm()
    if form.validate_on_submit():
        sub.admin_notes = form.admin_notes.data
        if form.decision.data == u'approve':
            sub.approve()
        else:
            sub.reject()
        sub.store()

        if form.decision.data == u'mute':
            user = sub.user
            user.is_muted = True
            user.store()

        if form.decision.data == u'approve':
            flash(u"The submission has been published to the leaderboard.",
                  'success')
        elif form.decision.data == u'reject':
            flash(u"The submission has been rejected.", 'error')
        elif form.decision.data == u'mute':
            flash(u"The submission has been rejected, and the user "
                   "responsible has been muted.", 'error')

        return redirect(url_for('challenges.review_queue'))

    return render_template("challenges/review-submission.html",
                           challenge=challenge, submission=sub,
                           form=form)

