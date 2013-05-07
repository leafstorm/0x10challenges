# -*- coding: utf-8 -*-
"""
zx10challenges.views
====================
This package contains all of the application's blueprints.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from .challenges import challenges
from .accounts import accounts

#: The items of `BLUEPRINTS` should either be actual `Blueprint` objects or
#: tuples of ``(blueprint, url_prefix)``.
BLUEPRINTS = (
    challenges,
    accounts
)
