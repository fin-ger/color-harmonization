# Copyright (C) 2016  David Bögelsack, Fin Christensen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from color_harmonization import global_variables
from color_harmonization.gui.assistant import Assistant

class Handler:
    def __init__ (self: 'Handler') -> None:
        pass

    def on_cancel (self: 'Handler', assistant: 'Gtk.Assistant', user_data: 'Any' = None) -> None:
        self.on_delete (None, None)

    def on_close (self: 'Handler', assistant: 'Gtk.Assistant', user_data: 'Any' = None) -> None:
        self.on_delete (None, None)

    def on_escape (self: 'Handler', assistant: 'Gtk.Assistant', user_data: 'Any' = None) -> None:
        self.on_delete (None, None)

    def on_delete (self: 'Handler', widget: 'Gtk.Widget', event: 'Gtk.Event',
                   user_data: 'Any' = None) -> None:
        global_variables.Application.assistant.stop ()

class Application:
    def __init__ (self: 'Application') -> None:
        self.assistant = Assistant (Handler ())

    def run (self: 'Application') -> int:
        return self.assistant.run ()
