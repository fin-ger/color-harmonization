#! /usr/bin/env python3

'''
Copyright (C) 2016  David Bögelsack, Fin Christensen

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import sys
import gi
gi.require_version ('Gtk', '3.0')

from typing import List
from color_harmonization import global_variables
from color_harmonization.application import Application

def main (argv: List[str]) -> int:
    global_variables.App = Application ()
    return global_variables.App.run ()

if __name__ == '__main__':
    sys.exit (main (sys.argv))
