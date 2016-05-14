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
from gi.repository import Gtk, Gdk
from typing import Any

class Handler:
    def __init__ (self: 'Handler') -> None:
        pass

    def on_cancel (self: 'Handler', assistant: Gtk.Assistant, user_data: Any = None) -> None:
        self.on_delete (None, None)

    def on_close (self: 'Handler', assistant: Gtk.Assistant, user_data: Any = None) -> None:
        self.on_delete (None, None)

    def on_escape (self: 'Handler', assistant: Gtk.Assistant, user_data: Any = None) -> None:
        self.on_delete (None, None)

    def on_delete (self: 'Handler', widget: Gtk.Widget, event: Gdk.Event,
                   user_data: 'Any' = None) -> None:
        global_variables.App.assistant.stop ()
