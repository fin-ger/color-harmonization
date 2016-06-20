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
import locale
import warnings
from gi.repository import Gtk, GdkPixbuf, GLib
from typing import List, Any, cast
from color_harmonization.handler import Handler
from color_harmonization.gui.gl_image import GLImage
from color_harmonization.gui.hue_sat_wheel_widget import HueSatWheelWidget
from color_harmonization.gui.gl_quad_renderer import GLQuadRenderer

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
        self.__selected_image_preview_box = self.__builder.get_object (
            "selected-image-preview"
        ) # type: Gtk.Grid
        self.__result_image_box = self.__builder.get_object (
            "harmonized-image"
        ) # type: Gtk.Box
        self.__progressbar = self.__builder.get_object (
            "harmonizing-progressbar"
        ) # type: Gtk.ProgressBar
        self.__save_button = self.__builder.get_object (
            "save-button"
        ) # type: Gtk.Button
        self.__images_box = self.__builder.get_object (
            "images-box"
        ) # type: Gtk.Box
        self.__harmonization_type_stack = self.__builder.get_object (
            "harmonization-type-stack"
        ) # type: Gtk.Stack
        self.__choose_image_box = self.__builder.get_object (
            "choose-image-box"
        ) # type: Gtk.Box

        harmonization_types = [
            "i-type", "V-type", "L-type", "I-type", "T-type", "Y-type", "X-type"
        ]
        self.hue_sat_wheels = [] # type: List[HueSatWheelWidget]
        for htype in harmonization_types:
            child = HueSatWheelWidget (sector = HueSatWheelWidget.sectors[htype])
            self.__harmonization_type_stack.add_named (child, htype)
            self.__harmonization_type_stack.child_set_property (child, "icon-name", htype)
            self.hue_sat_wheels.append (child)

        self.__unknown_svg = "color_harmonization/gui/icon/unknown.svg"
        self.__unknown_png = "color_harmonization/gui/icon/unknown.png"
        self.original_image = GLImage (3, 3)
        self.harmonized_image = GLImage (3, 3, 512, True)
        self.__result_image = GLImage (3, 3, 2048)
        self.__selected_image_preview = GLImage (3, 3)
        self.__selected_image_preview_box.attach (self.__selected_image_preview, 0, 0, 1, 1)
        self.__result_image_box.pack_start (self.__result_image, True, True, 0)
        self.__images_box.pack_start (self.original_image, True, True, 0)
        self.__images_box.pack_start (self.harmonized_image, True, True, 0)
        self.input_image = None # type: str

        self.back_btn = Gtk.Button.new_from_stock ("gtk-go-back")
        self.close_btn = Gtk.Button.new_from_stock ("gtk-close")
        self.back_btn.connect ("clicked", self.on_assistant_back)
        self.close_btn.connect ("clicked", self.on_assistant_close)
        self.close_btn.set_size_request (100, -1)
        self.back_btn.set_size_request (100, -1)

    def on_assistant_close (self: 'Assistant', button: Gtk.Button) -> None:
        self.assistant.close ()

    def on_assistant_back (self: 'Assistant', button: Gtk.Button) -> None:
        self.assistant.previous_page ()

    def apply_assistant_buttons (self: 'Assistant') -> None:
        headerbar = self.get_buttons_headerbar ()
        headerbar.pack_start (self.back_btn)
        headerbar.pack_end (self.close_btn)
        self.back_btn.show ()
        self.close_btn.show ()

    def disable_assistant_buttons (self: 'Assistant') -> None:
        self.back_btn.hide ()
        self.close_btn.hide ()

    def get_buttons_headerbar (self: 'Assistant'):
        label = Gtk.Label ()
        self.assistant.add_action_widget (label)
        headerbar = label.get_parent ()
        headerbar.remove (label)
        return headerbar

    def run (self: 'Assistant') -> int:
        self.assistant.show_all ()
        Gtk.main ()
        return 0

    def stop (self: 'Assistant') -> None:
        Gtk.main_quit ()

    def prepare_next_page (self: 'Assistant') -> None:
        if self.assistant.get_current_page () > 0:
            self.back_btn.set_sensitive (True)
        else:
            self.back_btn.set_sensitive (False)

        if self.assistant.get_current_page () == 2:
            self.__progressbar.set_fraction (0)
            self.assistant.set_page_complete (self.assistant.get_nth_page (2), False)
            self.start_harmonization ()

        if self.assistant.get_current_page () == 3:
            self.apply_assistant_buttons ()
        else:
            self.disable_assistant_buttons ()

    def start_harmonization (self: 'Assistant') -> None:
        self.__cancel_harmonization = False
        self.timeout_id = GLib.timeout_add (50, self.update_progress, None)

    def update_progress (self: 'Assistant', user_data: Any = None) -> bool:
        if self.__cancel_harmonization:
            return False

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
            self.__cancel_harmonization = True
            self.assistant.previous_page ()

        dialog.destroy ()

    def set_histogram (self: 'Assistant', hist: List[float]) -> None:
        for child in self.hue_sat_wheels:
            child.histogram = hist

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

    def open_images (self: 'Assistant') -> None:
        dialog = Gtk.FileChooserDialog (
            title = "Choose image", action = Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_filter (self.__builder.get_object ("image-filefilter"))
        dialog.set_select_multiple (True)
        dialog.set_transient_for (self.assistant)

        response = dialog.run ()

        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames ()

        dialog.destroy ()

        if response == Gtk.ResponseType.OK:
            print ("Selected files: {}".format (", ".join (filenames)))
            self.assistant.input_image = filenames[0]

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
            self.__selected_image_preview.set_path (self.__unknown_png)
        else:
            self.__selected_image_preview.set_path (self.__input_image)
            self.__result_image.set_path (self.__input_image)
            self.original_image.set_path (self.__input_image)
            self.harmonized_image.set_path (self.__input_image)
            self.assistant.set_page_complete (
                self.assistant.get_nth_page (self.assistant.get_current_page ()),
                True
            )
