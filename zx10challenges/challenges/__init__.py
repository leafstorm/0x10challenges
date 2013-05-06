# -*- coding: utf-8 -*-
"""
zx10challenges.challenges
=========================
This package contains all the challenges available to the site's users.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from collections import OrderedDict
from .numeric import Fibonacci
from .lists import BinarySearch

CHALLENGES = OrderedDict()

for challenge in [
    Fibonacci(),
    BinarySearch(),
]:
    CHALLENGES[challenge.id] = challenge
