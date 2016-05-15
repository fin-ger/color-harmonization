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

import abc

from gi.repository import Gtk, Gdk
from OpenGL import GL

class GLRenderer (metaclass = abc.ABCMeta):
    @property
    def gl_widget (self: 'GLRenderer') -> 'GLWidget':
        return self.__gl_widget

    @gl_widget.setter
    def gl_widget (self: 'GLRenderer', value: 'GLWidget') -> None:
        self.__gl_widget = value

    def make_current (self: 'GLRenderer') -> None:
        self.gl_widget.make_current ()

    @abc.abstractmethod
    def load (self: 'GLRenderer') -> None:
        pass

    @abc.abstractmethod
    def update (self: 'GLRenderer') -> None:
        pass

    @abc.abstractmethod
    def resize (self: 'GLRenderer', width: int, height: int) -> None:
        GL.glViewport (0, 0, width, height)

    @abc.abstractmethod
    def render (self: 'GLRenderer') -> None:
        GL.glClear (GL.GL_COLOR_BUFFER_BIT)
        GL.glClearColor (0, 0, 0, 0)

class GLWidget (Gtk.Overlay):
    def __init__ (self: 'GLWidget', renderer: GLRenderer,
                  gl_major_version: int, gl_minor_version: int) -> None:
        super ().__init__ ()

        self.renderer = renderer
        self.renderer.gl_widget = self

        self.gl_area = Gtk.GLArea ()
        self.gl_area.set_required_version (gl_major_version, gl_minor_version)
        self.gl_area.props.has_alpha = True
        self.gl_area.props.has_depth_buffer = False
        self.gl_area.props.auto_render = True
        self.gl_area.connect ('render', self.__handle_render)
        self.gl_area.connect ('realize', self.__handle_realize)
        self.gl_area.connect ('resize', self.__handle_resize)

        self.add_overlay (self.gl_area)
        self.props.expand = True

        self.__width = 400
        self.__height = 300

    def __handle_render (self: 'GLWidget', gl_area: Gtk.GLArea, context: Gdk.GLContext) -> None:
        self.renderer.render ()

    def __handle_realize (self: 'GLWidget', gl_area: Gtk.GLArea) -> None:
        self.renderer.load ()

    def __handle_resize (self: 'GLWidget', gl_area: Gtk.GLArea, width: int, height: int) -> None:
        self.__width = width
        self.__height = height
        self.renderer.resize (width, height)

    @property
    def width (self: 'GLWidget') -> int:
        return self.__width

    @property
    def height (self: 'GLWidget') -> int:
        return self.__height

    def make_current (self: 'GLWidget') -> None:
        self.gl_area.make_current ()
