# -*- coding: utf-8 -*-
"""
zx10challenges.application
==========================
This is the main entry point for 0x10challenges. It contains the app factory.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from flask import Flask, Markup
from markdown import markdown
from .models import manager
from .login import login_manager
from .views import BLUEPRINTS

def create_app(config=None, extras=None):
    # create application object
    app = Flask("zx10challenges")
    
    # configure application
    app.config.from_object("zx10challenges.defaults")
    if isinstance(config, dict):
        app.config.update(config)
    elif isinstance(config, str):
        app.config.from_pyfile(config)
    elif config is None:
        app.config.from_envvar('ZX10CHALLENGES_CONFIG')

    if isinstance(extras, dict):
        # extras is primarily for the use of the launcher
        app.config.update(extras)
    
    # setup extensions
    manager.setup(app)
    manager.sync(app)

    login_manager.init_app(app)

    for blueprint in BLUEPRINTS:
        if isinstance(blueprint, tuple):
            app.register_blueprint(blueprint[0], url_prefix=prefix[1])
        else:
            app.register_blueprint(blueprint)
    
    # template utilities, etc.
    @app.template_filter('markdown')
    def markdown_filter(text, **options):
        options.setdefault('format', 'html5')
        options.setdefault('safe_mode', 'escape')
        options.setdefault('extensions', ['extra'])
        return Markup(markdown(text, **options))
    
    @app.template_filter('items_sorted')
    def items_sorted_filter(d):
        items = d.items()
        items.sort(key=lambda (k, v): (len(k), k))
        return items

    return app
