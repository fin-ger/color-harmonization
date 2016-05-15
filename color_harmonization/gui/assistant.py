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

import glob
import os
import warnings
from gi.repository import Gtk, GdkPixbuf, GLib
from typing import List, Any
from color_harmonization.handler import Handler
from color_harmonization.gui.gl_image import GLImage

class Assistant:
    def __init__ (self: 'Assistant', handler: Handler) -> None:
        self.__load_icons ("color_harmonization/gui/icon")
        self.__builder = Gtk.Builder () # type: Gtk.Builder
        warnings.filterwarnings ('ignore')
        self.__builder.add_objects_from_file (
            "color_harmonization/gui/color-harmonization.glade",
            ("color-harmonization-assistant", "sector-chooser-list-store", "image-filefilter")
        )
        warnings.filterwarnings ('default')
        self.__builder.connect_signals (handler)
        self.assistant = self.__builder.get_object (
            "color-harmonization-assistant"
        ) # type: Gtk.Assistant
        self.assistant.set_wmclass (self.assistant.props.title, self.assistant.props.title)
        self.__selected_image_preview = self.__builder.get_object (
            "selected-image-preview"
        ) # type: Gtk.Image
        self.__result_image = self.__builder.get_object (
            "harmonized-image"
        ) # type: Gtk.Image
        self.__progressbar = self.__builder.get_object (
            "harmonizing-progressbar"
        ) # type: Gtk.ProgressBar
        self.__save_button = self.__builder.get_object (
            "save-button"
        ) # type: Gtk.Button
        self.__images_box = self.__builder.get_object (
            "images-box"
        ) # type: Gtk.Box
        self.__unknown_svg = "color_harmonization/gui/icon/unknown.svg"
        self.__unknown_png = "color_harmonization/gui/icon/unknown.png"
        self.original_image = GLImage (3, 3)
        self.harmonized_image = GLImage (3, 3)
        self.__images_box.pack_start (self.original_image, True, True, 0)
        self.__images_box.pack_start (self.harmonized_image, True, True, 0)
        self.input_image = None # type: str

    def run (self: 'Assistant') -> int:
        self.assistant.show_all ()
        Gtk.main ()
        return 0

    def stop (self: 'Assistant') -> None:
        Gtk.main_quit ()

    def prepare_next_page (self: 'Assistant') -> None:
        if self.assistant.get_current_page () == 2:
            self.assistant.commit ()
            self.start_harmonization ()

    def start_harmonization (self: 'Assistant') -> None:
        self.timeout_id = GLib.timeout_add (50, self.update_progress, None)

    def update_progress (self: 'Assistant', user_data: Any = None) -> bool:
        new_value = self.__progressbar.get_fraction () + 0.01

        if new_value > 1:
            self.assistant.set_page_complete (
                self.assistant.get_nth_page (self.assistant.get_current_page ()),
                True
            )
            self.assistant.next_page ()
            return False

        self.__progressbar.set_fraction (new_value)
        return True

    def cancel_harmonization (self: 'Assistant') -> None:
        builder = Gtk.Builder () # type: Gtk.Builder
        warnings.filterwarnings ('ignore')
        builder.add_objects_from_file (
            "color_harmonization/gui/color-harmonization.glade",
            ("cancel-messagedialog",)
        )
        warnings.filterwarnings ('default')
        dialog = builder.get_object ("cancel-messagedialog") # type: Gtk.MessageDialog
        dialog.set_transient_for (self.assistant)
        response = dialog.run () # type: int

        if response == Gtk.ResponseType.YES:
            self.stop ()

        dialog.destroy ()

    def save_image (self: 'Assistant') -> None:
        dialog = Gtk.FileChooserDialog (
            title = "Choose a filename", action = Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        dialog.set_filter (self.__builder.get_object ("image-filefilter"))
        dialog.set_transient_for (self.assistant)
        response = dialog.run ()

        if response == Gtk.ResponseType.OK:
            newfile = dialog.get_filename ()

        dialog.destroy ()

        if response == Gtk.ResponseType.OK:
            print ("File save location is '{}'".format (newfile))

    def __load_icons (self: 'Assistant', folder: str, size: int = 16) -> None:
        icons = {
            os.path.splitext (os.path.basename (f))[0]: GdkPixbuf.Pixbuf.new_from_file_at_scale (
                f, size, size, True
            ) for f in
            glob.glob ("{}/*.svg".format (folder))
        }
        for icon, pixbuf in icons.items ():
            Gtk.IconTheme.get_default ().add_builtin_icon (icon, size, pixbuf)

    @property
    def input_image (self: 'Assistant') -> str:
        return self.__input_image

    @input_image.setter
    def input_image (self: 'Assistant', value: str) -> None:
        self.__input_image = value

        if self.__input_image is None:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale (self.__unknown_svg, 400, 200, True)
            self.__selected_image_preview.set_from_pixbuf (pixbuf)
            self.__result_image.set_from_pixbuf (pixbuf)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale (self.__input_image, 400, 200, True)
            self.__selected_image_preview.set_from_pixbuf (pixbuf)
            self.__result_image.set_from_pixbuf (pixbuf)
            self.original_image.set_path (self.__input_image)
            self.harmonized_image.set_path (self.__input_image)
            self.assistant.set_page_complete (
                self.assistant.get_nth_page (self.assistant.get_current_page ()),
                True
            )
