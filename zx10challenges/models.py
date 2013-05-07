# -*- coding: utf-8 -*-
"""
zx10challenges.models
=====================
This contains the data models for 0x10challenges. Some of these exist only
in code, others are stored in a CouchDB database.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from abc import ABCMeta, abstractmethod
from flask.ext.couchdb import (CouchDBManager, Document, Mapping,
                               TextField, IntegerField, BooleanField,
                               DecimalField, DateTimeField,
                               DictField, ListField)


manager = CouchDBManager(auto_sync=False)


class Challenge(object):
    """
    This is the base class that each challenge inherits from.
    """
    __metaclass__ = ABCMeta

    #: The ID of this challenge. This should be unique, and is used to
    #: look up the challenge from the URL etc.
    id = None

    #: The version of this challenge. This is a 2-tuple: the first item
    #: is the "spec version," which indicates whether code can be reused.
    #: The second item is the "results version," which indicates whether the
    #: result fields of a `Submission` can be reused.
    #: Versions start at 1. When the spec version is incremented, the results
    #: version should reset to 1.
    version = (0, 0)

    @property
    def spec_ver(self):
        return self.version[0]

    @property
    def results_ver(self):
        return self.version[1]

    #: Whether this challenge is open for attempts.
    #: If it isn't, then it will only be visible in a user's "My Submissions"
    #: page.
    open = True

    #: The title of this challenge.
    title = None

    #: A brief, one-imperative-sentence description of this challenge.
    objective = None

    #: A more detailed description which specifies exactly what the challenge
    #: is graded on.
    spec = None

    #: The metrics that the user's program will be evaluated on.
    metrics = ()

    #: The metrics that individual test cases are evaluated on.
    case_metrics = ()

    def create_submission(self):
        """
        Creates a blank submission object for this challenge.
        """
        return Submission(challenge_id=self.id, spec_ver=self.version[0],
                          results_ver=self.version[1])

    @abstractmethod
    def evaluate(self, submission):
        """
        This accepts a user's submission, evaluates it, and fills out the
        report fields.

        :param submission: A `Submission` object with the assembly code and
                           notes filled in.
        """
        pass


class StopEvaluating(BaseException):
    """
    This exception indicates that a challenge has failed automatically
    (or, rarely, passed automatically) and the results should be reported
    now.
    """


class Metric(object):
    """
    This represents a metric that can apply to a program.
    """
    def __init__(self, id, name, pattern):
        self.id = id
        self.name = name
        self.pattern = pattern

    def format(self, n):
        return self.pattern.format(n)


class TestCase(Mapping):
    title = TextField()
    passed = BooleanField(default=False)

    input = DictField()
    expected_output = DictField()
    actual_output = DictField()

    metrics = DictField()
    comments = ListField(TextField())
    violations = ListField(TextField())


class Submission(Document):
    doc_type = 'submission'

    # Submission metadata
    challenge_id = TextField()
    spec_ver = IntegerField()
    results_ver = IntegerField()

    @property
    def challenge_version(self):
        return (self.spec_ver, self.results_ver)

    @challenge_version.setter
    def _set_challenge_version(self, version):
        if len(version) != 2:
            raise TypeError("Version should be a 2-tuple")
        self.spec_ver = version[0]
        self.results_ver = version[1]
    del _set_challenge_version

    # Submitter metadata
    user_id = TextField()
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
    published = BooleanField(default=False)
    submit_date = DateTimeField()
    approved = BooleanField(default=False)
    admin_notes = TextField()

    def submit(self):
        self.submitted = True
        self.submit_date = datetime.datetime.utcnow()

    def approve(self):
        self.approved = True
