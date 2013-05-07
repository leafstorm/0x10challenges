# -*- coding: utf-8 -*-
"""
zx10challenges.launcher
=======================
This is a WSGI launcher for Heroku-like environments.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
import logging
import sys
from logging import StreamHandler
from .application import create_app

app = create_app()
app.logger.addHandler(StreamHandler(sys.stderr))
