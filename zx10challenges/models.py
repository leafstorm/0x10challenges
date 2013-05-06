# -*- coding: utf-8 -*-
"""
zx10challenges.models
=====================
This contains 0x10challenge's CouchDB document classes.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from flask.ext.couchdb import (CouchDBManager, Document, Mapping,
                               TextField, IntegerField, BooleanField,
                               DecimalField, DateTimeField,
                               DictField, ListField)


manager = CouchDBManager(auto_sync=False)

class TestCase(Mapping):
    title = TextField()
    passed = BooleanField(default=False)

    input = TextField()
    expected_output = TextField()
    actual_output = TextField()

    metrics = DictField()
    comments = ListField(TextField())
    violations = ListField(TextField())


class Submission(Document):
    doc_type = 'submission'

    # Submission metadata
    challenge_id = TextField()
    user_email = TextField()
    user_nickname = TextField()

    # Submission content
    assembly = TextField()
    notes = TextField()

    # Results from evaluating this submission
    passed = BooleanField(default=False)
    caption = TextField()
    test_cases = ListField(DictField(TestCase))

    metrics = DictField()
    comments = ListField(TextField())
    violations = ListField(TextField())

    # Control data for the hall of fame
    submitted = BooleanField(default=False)
    submit_date = DateTimeField()
    published = BooleanField(default=False)
    admin_notes = TextField()
