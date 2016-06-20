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

import numpy
import threading
import warnings

from OpenGL import GL
from pyrr import Matrix44
from PIL import Image
from color_harmonization.gui.gl_widget import GLWidget, GLRenderer
from color_harmonization import global_variables

DEBUG = False

class GLQuadRenderer (GLRenderer):
    scale = 2**14
    log_scale = numpy.log2 (256 * 2**14)

    def __init__ (self: 'GLQuadRenderer', view_size: int = 512,
                  create_histogram: bool = False, size: int = 300) -> None:
        super ().__init__ ()
        self.__do_harmonization = False
        self.__new_texture = None # type: Image
        self.__view_size = view_size
        self.__loaded = False
        self.__create_histogram = create_histogram
        self.__size = size

    def load (self: 'GLQuadRenderer') -> None:
        self.make_current ()

        GL.glDisable (GL.GL_CULL_FACE)

        self.program = GL.glCreateProgram ()
        self.vertex_shader = GL.glCreateShader (GL.GL_VERTEX_SHADER)
        self.fragment_shader = GL.glCreateShader (GL.GL_FRAGMENT_SHADER)

        vs_file = open ("color_harmonization/gui/glsl/vertex_shader.vsh", 'r')
        vs_code = vs_file.read ()
        vs_file.close ()
        fs_file = open ("color_harmonization/gui/glsl/fragment_shader.fsh", 'r')
        fs_code = fs_file.read ()
        fs_file.close ()

        GL.glShaderSource (self.vertex_shader, vs_code)
        GL.glShaderSource (self.fragment_shader, fs_code)

        GL.glCompileShader (self.vertex_shader)

        if DEBUG:
            error_log = GL.glGetShaderInfoLog (self.vertex_shader)
            print ("Vertex shader: {}".format (error_log.decode ()))

        GL.glCompileShader (self.fragment_shader)

        if DEBUG:
            error_log = GL.glGetShaderInfoLog (self.fragment_shader)
            print ("Fragment shader: {}".format (error_log.decode ()))

        GL.glAttachShader (self.program, self.vertex_shader)
        GL.glAttachShader (self.program, self.fragment_shader)

        GL.glLinkProgram (self.program)

        if DEBUG:
            error_log = GL.glGetProgramInfoLog (self.program)
            print ("Program link: {}".format (error_log.decode ()))

        self.array_buffer = GL.glGenBuffers (1)
        self.vertex_array = GL.glGenVertexArrays (1)

        data = numpy.array ([0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                             0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                             1.0, 0.0, 1.0, 1.0, 0.0, 0.0,
                             1.0, 1.0, 1.0, 0.0, 0.0, 0.0],
                            dtype = numpy.float32)

        GL.glBindVertexArray (self.vertex_array)
        GL.glBindBuffer (GL.GL_ARRAY_BUFFER, self.array_buffer)
        GL.glBufferData (GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray (0)
        GL.glVertexAttribPointer (0, 2, GL.GL_FLOAT, False, 24, GL.ctypes.c_void_p (0))
        GL.glEnableVertexAttribArray (1)
        GL.glVertexAttribPointer (1, 2, GL.GL_FLOAT, False, 24, GL.ctypes.c_void_p (8))
        GL.glEnableVertexAttribArray (2)
        GL.glVertexAttribPointer (2, 2, GL.GL_FLOAT, False, 24, GL.ctypes.c_void_p (16))

        GL.glUseProgram (self.program)

        self.__uniform_world = GL.glGetUniformLocation (self.program, "WorldMatrix")
        self.__uniform_projection = GL.glGetUniformLocation (self.program, "ProjectionMatrix")
        self.__uniform_texture = GL.glGetUniformLocation (self.program, "Texture")
        self.__uniform_data_texture = GL.glGetUniformLocation (self.program, "DataTexture")
        self.__uniform_do_harmonization = GL.glGetUniformLocation (self.program, "DoHarmonization")

        self.__texture = 0
        self.__data_texture = 0

        GL.glUniformMatrix4fv (self.__uniform_projection, 1, False,
                               Matrix44.orthogonal_projection (0, 1, 0, 1, 0, 1))
        GL.glUniform1i (self.__uniform_do_harmonization, self.__do_harmonization)

    def load_texture (self: 'GLQuadRenderer', path: str) -> None:
        self.__image_loader_thread = threading.Thread (
            target = self.__image_loader, args = [path]
        )
        self.__image_loader_thread.start ()

    def __image_loader (self: 'GLQuadRenderer', path: str) -> None:
        warnings.filterwarnings ('ignore')
        with Image.open (path) as f:
            f.thumbnail ((self.__view_size, self.__view_size))
            img = f.convert ("RGBA")

            if self.__create_histogram:
                hsv = f.convert ("HSV")
                h = hsv.getdata (band = 0)
                s = hsv.getdata (band = 1)

                hist = [0.0] * 256
                for idx, hue in enumerate (h):
                    hist[hue] += s[idx]

                hist = numpy.log2 ([
                    (val / (hsv.size[0] * hsv.size[1])) * GLQuadRenderer.scale + 1 for val in hist
                ])
                hist = [val / GLQuadRenderer.log_scale for val in hist]

                global_variables.App.assistant.set_histogram (hist)

            self.__image_width = img.size[0]
            self.__image_height = img.size[1]
            self.gl_widget.props.width_request = self.__size
            self.gl_widget.props.height_request = img.size[1] / float (img.size[0]) * self.__size
            self.__new_texture = numpy.array (list (img.getdata ()), numpy.uint8)
            warnings.filterwarnings ('default')

        timer = threading.Timer (0.01, self.gl_widget.gl_area.queue_draw)
        timer.start ()

        self.__loaded = True

    def __load_texture (self: 'GLQuadRenderer') -> None:
        img_data = self.__new_texture

        GL.glActiveTexture (GL.GL_TEXTURE0)
        GL.glBindTexture (GL.GL_TEXTURE_2D, 0)

        if self.__texture > 0:
            GL.glDeleteTextures ([self.__texture])

        self.__texture = GL.glGenTextures (1)

        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__texture)
        GL.glTexImage2D (GL.GL_TEXTURE_2D, 0, GL.GL_RGBA,
                         self.__image_width, self.__image_height, 0,
                         GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)

        GL.glGenerateMipmap (GL.GL_TEXTURE_2D)

        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR_MIPMAP_LINEAR)
        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri (GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

        self.resize (self.gl_widget.width, self.gl_widget.height)

        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__texture)
        GL.glUniform1i (self.__uniform_texture, 0)

        GL.glActiveTexture (GL.GL_TEXTURE1)
        self.__data = numpy.zeros ((self.__image_width * self.__image_height, 4),
                                   dtype = numpy.float32)

        if self.__data_texture > 0:
            GL.glDeleteTextures ([self.__data_texture])

        self.__data_texture = GL.glGenTextures (1)
        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__data_texture)
        GL.glTexImage2D (GL.GL_TEXTURE_2D, 0, GL.GL_RGBA32F,
                         self.__image_width, self.__image_height, 0,
                         GL.GL_RGBA, GL.GL_FLOAT, self.__data)

        GL.glGenerateMipmap (GL.GL_TEXTURE_2D)
        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__data_texture)
        GL.glUniform1i (self.__uniform_data_texture, 1)

    def resize (self: 'GLQuadRenderer', width: int, height: int) -> None:
        super ().resize (width, height)

        if not self.__loaded:
            return

        y = self.__image_height / self.__image_width * \
            self.gl_widget.width / self.gl_widget.height

        x = self.__image_width / self.__image_height * \
            self.gl_widget.height / self.gl_widget.width

        if self.gl_widget.height * self.__image_width / self.__image_height > self.gl_widget.width:
            self.world = Matrix44.from_scale ([1, y, 1]) * \
                         Matrix44.from_translation ([0, (1 - y) / 2, 0])
        else:
            self.world = Matrix44.from_scale ([x, 1, 1]) * \
                         Matrix44.from_translation ([(1 - x) / 2, 0, 0])

        GL.glUniformMatrix4fv (self.__uniform_world, 1, False, self.world)

    def render (self: 'GLQuadRenderer') -> None:
        if not self.__loaded:
            return

        if self.__new_texture is not None:
            self.__load_texture ()
            self.__new_texture = None

        super ().render ()

        GL.glActiveTexture (GL.GL_TEXTURE0)
        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__texture)
        GL.glActiveTexture (GL.GL_TEXTURE1)
        GL.glBindTexture (GL.GL_TEXTURE_2D, self.__data_texture)
        GL.glDrawArrays (GL.GL_TRIANGLE_STRIP, 0, 4)

    def update (self: 'GLQuadRenderer') -> None:
        super ().update ()
