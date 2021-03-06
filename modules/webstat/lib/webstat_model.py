# -*- coding: utf-8 -*-
#
## This file is part of Invenio.
## Copyright (C) 2011, 2012 CERN.
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
## 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""
webstat database models.
"""

# General imports.
from invenio.sqlalchemyutils import db

# Create your models here.

class StaEVENT(db.Model):
    """Represents a StaEVENT record."""
    def __init__(self):
        pass
    __tablename__ = 'staEVENT'
    id = db.Column(db.String(255), nullable=False,
                primary_key=True)
    number = db.Column(db.SmallInteger(2, unsigned=True, zerofill=True),
                nullable=False, autoincrement=True, primary_key=True,
                unique=True)
    name = db.Column(db.String(255), nullable=True)
    creation_time = db.Column(db.TIMESTAMP, nullable=False,
                server_default=db.func.current_timestamp())
    cols = db.Column(db.String(255), nullable=True)

__all__ = ['StaEVENT']
