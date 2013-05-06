# -*- coding: utf-8 -*-
"""
zx10challenges.launcher
=======================
This is a WSGI launcher for Heroku-like environments.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from .application import create_app

app = create_app()
