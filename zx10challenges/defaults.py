# -*- coding: utf-8 -*-
"""
zx10challenges.defaults
=======================
This contains the default settings for the application.
(Copy this and delete the header, and you can use it as a config file.)

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""

#: Whether to run the application in debug mode or not. (Most of the time,
#: this should be `False`. Running this with `True` in production is a HUGE
#: security loophole.)
DEBUG = False

#: The secret key used to sign sessions. You can generate one with the command
#: ``python -c "import os; print(repr(os.urandom(20)))"``.
SECRET_KEY = 'Not actually secret'

#: The name of the cookie used to store user sessions.
SESSION_COOKIE_NAME = '0x10challenges_session'

#: The server containing this installation's CouchDB database. If
#: authentication is necessary, just put it in the URL.
COUCHDB_SERVER = 'http://localhost:5984/'

#: The name of the database to use on COUCHDB_SERVER.
COUCHDB_DATABASE = 'zx10challenges'
