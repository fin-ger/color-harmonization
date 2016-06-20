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

from gi.repository import Gtk
from color_harmonization.gui.gl_quad_renderer import GLQuadRenderer
from color_harmonization.gui.gl_widget import GLWidget
from typing import cast

class GLImage (GLWidget):
    def __init__ (self: 'GLImage', gl_major_version: int, gl_minor_version: int,
                  view_size: int = 512, create_histogram: bool = False) -> None:
        super ().__init__ (GLQuadRenderer (view_size, create_histogram),
                           gl_major_version, gl_minor_version)

    def set_path (self: 'GLImage', path: str) -> None:
        cast (GLQuadRenderer, self.renderer).load_texture (path)
