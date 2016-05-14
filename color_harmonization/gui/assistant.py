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

import gi
import warnings

gi.require_version ('Gtk', '3.0')
from gi.repository import Gtk

class Assistant:
    def __init__ (self: 'Assistant', handler: 'Handler') -> None:
        self.builder = Gtk.Builder ()
        warnings.filterwarnings ('ignore')
        self.builder.add_from_file ("color_harmonization/gui/color-harmonization.glade")
        warnings.filterwarnings ('default')
        self.builder.connect_signals (handler)
        self.assistant = self.builder.get_object ("color-harmonization-assistant")

    def run (self: 'Assistant') -> int:
        self.assistant.show_all ()
        Gtk.main ()
        return 0

    def stop (self: 'Assistant') -> None:
        Gtk.main_quit ()
