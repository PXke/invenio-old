# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
    invenio.ext.menualchemy
    ----
    This extension allows creation of menus organised in a tree structure.
    Those menus can be then displayed using templates.
"""

from flask import url_for, current_app
from werkzeug import LocalProxy

CONDITION_TRUE = (lambda: True)
CONDITION_FALSE = (lambda: False)


class MenuAlchemy(object):
    """Extension object for invenio.ext.menualchemy"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['menualchemy'] = MenuEntryMixin('')
        app.context_processor(lambda: dict(
            current_menu=current_menu))

    @staticmethod
    def root():
        """
        :return: Root entry of current application's menu.
        """
        return current_app.extensions['menualchemy']

    @staticmethod
    def register_menu(blueprint, path, text, order=0,
                      endpoint_arguments_constructor=None,
                      active_when=CONDITION_FALSE,
                      visible_when=CONDITION_TRUE):
        """Decorate endpoints that should be displayed in a menu.

        :param blueprint: Blueprint which owns the function.
        :param path: Path to this item in menu hierarchy,
            for example 'main.category.item'.
        :param text: Text displayed as link.
        :param order: Index of item among other items in the same menu.
        :param endpoint_arguments_constructor: Function returning dict of
            arguments passed to url_for when creating the link.
        :param active_when: Function returning True when the item
            should be displayed as active.
        :param visible_when: Function returning True when this item
            should be displayed.
        """

        #Decorator function
        def menu_decorator(f):
            endpoint = blueprint.name + '.' + f.__name__

            @blueprint.before_app_first_request
            def _register_menu_item():
                item = current_menu.submenu(path)
                item.register(endpoint, text, order,
                              endpoint_arguments_constructor,
                              active_when, visible_when)
            return f

        return menu_decorator


class MenuEntryMixin(object):
    """Represents a entry node in the menu tree.

    Provides information for displaying links (text, url, visible, active).
    Navigate the hierarchy using :meth:`children` and :meth:`submenu`.
    """

    def __init__(self, name):
        self.name = name
        self._child_entries = dict()
        self._endpoint = None
        self._text = None
        self._order = 0
        self._endpoint_arguments_constructor = None
        self._active_when = CONDITION_FALSE
        self._visible_when = CONDITION_TRUE

    def register(self, endpoint, text, order=0,
                 endpoint_arguments_constructor=None,
                 active_when=CONDITION_FALSE,
                 visible_when=CONDITION_TRUE):
        """Assigns endpoint and display values."""
        self._endpoint = endpoint
        self._text = text
        self._order = order
        self._endpoint_arguments_constructor = endpoint_arguments_constructor
        self._active_when = active_when or CONDITION_FALSE
        self._visible_when = visible_when or CONDITION_TRUE

    def submenu(self, path):
        """Returns submenu placed at the given path in the hierarchy.

        If it does not exist, a new one is created.
        Returns None if path string is invalid.

        :param path: Path to submenu as a string 'qua.bua.cua'
        :return: Submenu placed at the given path in the hierarchy.
        """

        if not path:
            return self

        (path_head, dot, path_tail) = path.partition('.')

        # Create the entry if it does not exist
        if path_head not in self._child_entries:
            self._child_entries[path_head] = MenuEntryMixin(path_head)

        next_entry = self._child_entries[path_head]

        if path_tail:
            return next_entry.submenu(path_tail)
        else:
            # that was the last part of the path
            return next_entry

    def hide(self):
        """Makes the entry always hidden."""
        self._visible_when = CONDITION_FALSE

    @property
    def order(self):
        return self._order

    @property
    def children(self):
        return sorted(self._child_entries.values(),
                      key=lambda entry: getattr(entry, 'order', 0))

    @property
    def text(self):
        return self._text or 'Menu item not initialised'

    @property
    def url(self):
        if not self._endpoint:
            return '#'

        if self._endpoint_arguments_constructor:
            return url_for(self._endpoint,
                           **self._endpoint_arguments_constructor())
        return url_for(self._endpoint)

    @property
    def active(self):
        return self._active_when()

    @property
    def visible(self):
        return self._text is not None and self._visible_when()


## Global object that is proxy to the current application menu.
current_menu = LocalProxy(MenuAlchemy.root)

## Decorator for menu item registration.
register_menu = MenuAlchemy.register_menu

__all__ = ['current_menu', 'register_menu', 'MenuAlchemy']