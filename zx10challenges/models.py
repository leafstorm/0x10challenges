# -*- coding: utf-8 -*-
"""
zx10challenges.models
=====================
This contains the data models for 0x10challenges. Some of these exist only
in code, others are stored in a CouchDB database.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
import datetime
from abc import ABCMeta, abstractmethod
from flask.ext.couchdb import (CouchDBManager, Document, Mapping,
                               TextField, IntegerField, BooleanField,
                               DecimalField, DateTimeField,
                               DictField, ListField, ViewField)
from flask.ext.login import UserMixin


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

    def get_leaderboards(self):
        """
        Gets all the leaderboards for a challenge.
        """
        boards = []
        for metric in self.metrics:
            low_key = [self.id, self.spec_ver, self.results_ver, metric.id]
            high_key = low_key + [{}]
            if metric.descends:
                options = {'startkey': high_key, 'endkey': low_key,
                           'descending': True}
            else:
                options = {'startkey': low_key, 'endkey': high_key,
                           'descending': False}
            subs = Submission.approved_by_metric(**options)
            boards.append((metric, subs))
        return boards

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
    This represents a metric that a submission or test case can be ranked on.
    """
    def __init__(self, id, name, pattern, descends=False):
        self.id = id
        self.name = name
        self.pattern = pattern
        self.descends = descends

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
    def challenge_version(self, version):
        if len(version) != 2:
            raise TypeError("Version should be a 2-tuple")
        self.spec_ver = version[0]
        self.results_ver = version[1]

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

    # Review information
    approved = BooleanField(default=False)
    needs_review = BooleanField(default=True)
    review_date = DateTimeField()
    admin_notes = TextField()

    @property
    def user(self):
        if self.user_id:
            return User.load(self.user_id)
        else:
            return None

    @user.setter
    def user(self, user):
        self.user_id = user.id
        self.user_nickname = user.nickname
        if user.is_muted:
            self.reject()

    def submit(self):
        self.submitted = True
        self.submit_date = datetime.datetime.utcnow()

    def approve(self):
        self.approved = True
        self.needs_review = False
        self.review_date = datetime.datetime.utcnow()

    def reject(self):
        self.approved = False
        self.needs_review = False
        self.review_date = datetime.datetime.utcnow()

    # Query methods
    @classmethod
    def get_review_queue(cls):
        return cls.review_queue().rows

    # Views
    all_by_challenge = ViewField('submissions', '''\
        function (doc) {
            if (doc.doc_type == 'submission') {
                emit([doc.challenge_id, doc.spec_ver, doc.results_ver,
                      doc.submit_date], null);
            }
        }''', include_docs=True)

    all_by_user = ViewField('submissions', '''\
        function (doc) {
            if (doc.doc_type == 'submission') {
                emit([doc.user_id, doc.submit_date]);
            }
        }''', include_docs=True)

    approved_by_metric = ViewField('submissions', '''\
        function (doc) {
            if (doc.doc_type == 'submission' && doc.approved) {
                for (var metric_id in doc.metrics) {
                    if (doc.metrics.hasOwnProperty(metric_id)) {
                        emit([doc.challenge_id, doc.spec_ver, doc.results_ver,
                              metric_id, doc.metrics[metric_id]], null);
                    }
                }
            }
        }''', include_docs=True)

    review_queue = ViewField('submissions', '''\
        function (doc) {
            if (doc.doc_type == 'submission' && doc.needs_review) {
                emit(doc.submit_date, null);
            }
        }''', include_docs=True)


manager.add_document(Submission)


class User(Document, UserMixin):
    """
    Contains information about a registered user of the site.
    """
    doc_type = 'user'

    #: The user's email.
    email = TextField()

    #: The nickname that the user has chosen for themself.
    nickname = TextField()

    #: The date that the user first joined on.
    join_date = DateTimeField(default=datetime.datetime.utcnow)

    #: If this is `True`, the user has been disabled.
    #: This prevents them from logging in.
    #: This is intended for defunct accounts.
    is_disabled = BooleanField(default=False)

    #: If this is `True`, the user has been muted.
    #: If you are muted, your submissions will automatically be denied.
    #: This is intended for spambots and harassers.
    is_muted = BooleanField(default=False)

    #: If this is `True`, the user is an administrator.
    is_admin = BooleanField(default=False)

    @classmethod
    def create(cls, email):
        nickname = email[:email.index("@")]
        return cls(email=email, nickname=nickname)

    @classmethod
    def get_by_email(cls, email):
        results = cls.by_email[email]
        if not len(results):
            return None
        else:
            return results.rows[0]

    @classmethod
    def get_or_create(cls, email):
        user = cls.get_by_email(email)
        if user is None:
            user = cls.create(email)
            user.store()
        return user

    def is_active(self):
        return not self.is_disabled

    def get_submissions(self):
        return Submission.all_by_user(startkey=[self.id, {}], endkey=[self.id],
                                      descending=True).rows

    by_email = ViewField('users', '''\
        function (doc) {
            if (doc.doc_type == 'user') {
                emit(doc.email, null);
            }
        }''', include_docs=True)

manager.add_document(User)

