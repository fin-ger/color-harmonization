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

import warnings
from gi.repository import Gtk, GdkPixbuf
from typing import TypeVar
from color_harmonization.handler import Handler

class Assistant:
    def __init__ (self: 'Assistant', handler: Handler) -> None:
        self.builder = Gtk.Builder () # type: Gtk.Builder
        warnings.filterwarnings ('ignore')
        self.builder.add_from_file ("color_harmonization/gui/color-harmonization.glade")
        warnings.filterwarnings ('default')
        self.builder.connect_signals (handler)
        self.assistant = self.builder.get_object (
            "color-harmonization-assistant"
        ) # type: Gtk.Assistant
        self.selected_image_preview = self.builder.get_object (
            "selected-image-preview"
        ) # type: Gtk.Image
        self.assistant.set_wmclass (self.assistant.props.title, self.assistant.props.title)
        self.__input_image = None # type: str

    def run (self: 'Assistant') -> int:
        self.assistant.show_all ()
        Gtk.main ()
        return 0

    def stop (self: 'Assistant') -> None:
        Gtk.main_quit ()

    @property
    def input_image (self: 'Assistant') -> str:
        return self.__input_image

    @input_image.setter
    def input_image (self: 'Assistant', value: str) -> None:
        self.__input_image = value
        self.selected_image_preview.set_from_pixbuf (
            GdkPixbuf.Pixbuf.new_from_file_at_scale (self.__input_image, 200, 200, True)
        )

        if self.__input_image is not None:
            self.assistant.set_page_complete (
                self.assistant.get_nth_page (self.assistant.get_current_page ()),
                True
            )
