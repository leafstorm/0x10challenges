# -*- coding: utf-8 -*-
"""
zx10challenges.manager
======================
This contains commands for the management script.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from flask import current_app
from flask.ext.script import Manager
from .application import create_app

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
