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

import math
import numpy
import colorsys
import cairocffi
import cairo

from gi.repository import Gtk
from typing import List

DEFAULT_SIZE = 200
DEFAULT_RING_WIDTH = 10

def _UNSAFE_pycairo_context_to_cairocffi (pycairo_context):
    # Sanity check. Continuing with another type would probably segfault.
    if not isinstance(pycairo_context, cairo.Context):
        raise TypeError('Expected a cairo.Context, got %r' % pycairo_context)

    # On CPython, id() gives the memory address of a Python object.
    # pycairo implements Context as a C struct:
    #     typedef struct {
    #         PyObject_HEAD
    #         cairo_t *ctx;
    #         PyObject *base;
    #     } PycairoContext;
    # Still on CPython, object.__basicsize__ is the size of PyObject_HEAD,
    # ie. the offset to the ctx field.
    # ffi.cast() converts the integer address to a cairo_t** pointer.
    # [0] dereferences that pointer, ie. read the ctx field.
    # The result is a cairo_t* pointer that cairocffi can use.
    return cairocffi.Context._from_pointer (
        cairocffi.ffi.cast (
            'cairo_t **',
            id (pycairo_context) + object.__basicsize__
        )[0],
        incref=True
    )

class HueSatWheelWidget (Gtk.Misc):
    __gtype_name__ = "HueSatWheelWidget"

    sectors = {
        "i-type": ([0.05], [0.]),
        "V-type": ([0.26], [0.]),
        "L-type": ([0.05, 0.22], [0., 0.25]),
        "I-type": ([0.05, 0.05], [0., 0.5]),
        "T-type": ([0.5], [0.]),
        "Y-type": ([0.26, 0.05], [0., 0.5]),
        "X-type": ([0.26, 0.26], [0., 0.5])
    }

    def __init__ (self: 'HueSatWheelWidget', *args, **kwargs) -> None:
        self.__hist = [0.0] * 256
        self.ring_width = kwargs["ring-width"] if "ring-width" in kwargs else DEFAULT_RING_WIDTH
        self.size = kwargs["size"] if "size" in kwargs else DEFAULT_SIZE
        self.sector = kwargs["sector"] if "sector" in kwargs else HueSatWheelWidget.sectors["i-type"]
        self.rotation = kwargs["rotation"] if "rotation" in kwargs else -numpy.pi / 2

        kwargs.pop ("ring-width", None)
        kwargs.pop ("size", None)
        kwargs.pop ("sector", None)
        kwargs.pop ("rotation", None)

        super ().__init__ (*args, **kwargs)
        self.set_size_request (self.size, self.size)

    def __draw_sector (self: 'HueSatWheelWidget', cr: cairocffi.Context,
                       center_x: float, center_y: float) -> None:
        cr.save ()
        cr.set_line_width (1)

        offset = self.rotation

        for idx, sector in enumerate (self.sector[0]):
            half_angle = 2 * numpy.pi * sector / 2
            offset += self.sector[1][idx] * 2 * numpy.pi
            cr.set_source_rgba (0, 0, 0, 1)
            cr.move_to (center_x, center_y)
            cr.arc (center_x, center_y, (self.size - 2) / 2.,
                    offset - half_angle, half_angle + offset)
            cr.line_to (center_x, center_y)
            cr.stroke_preserve ()
            cr.set_source_rgba (0, 0, 0, 0.25)
            cr.fill ()

        cr.restore ()

    def do_draw (self: 'HueSatWheelWidget', pycairo_cr: cairo.Context) -> bool:
        cr = _UNSAFE_pycairo_context_to_cairocffi (pycairo_cr)
        cr.set_source_rgba (0, 0, 0, 0)
        cr.paint ()

        width = self.get_allocated_width ()
        height = self.get_allocated_height ()

        center_x = width / 2.
        center_y = height / 2.

        outer = (self.size - 4) / 2.
        inner = outer - self.ring_width

        stride = cairocffi.ImageSurface.format_stride_for_width (cairocffi.FORMAT_ARGB32, width)
        buf = numpy.empty (int (height * stride), dtype = numpy.uint8)

        for y in range (height):
            idx = y * width * 4

            dy = -(y - center_y)

            for x in range (width):
                dx = x - center_x

                dist = dx * dx + dy * dy

                angle = math.atan2 (dy, dx)

                if angle < 0:
                    angle += 2 * numpy.pi

                hue = angle / (2 * numpy.pi)

                hue_idx = int ((angle + 2 * numpy.pi / 3) / (2 * numpy.pi) * 255)
                hue_idx = hue_idx % 256

                if dist < ((inner - 1) ** 2) * (1 - self.__hist[255 - hue_idx]) or \
                   dist > ((outer + 1) ** 2):
                    buf[idx + 0] = 0
                    buf[idx + 1] = 0
                    buf[idx + 2] = 0
                    buf[idx + 3] = 0
                    idx += 4
                    continue

                r, g, b = colorsys.hsv_to_rgb (hue, 1.0, 1.0)
                a = 255

                buf[idx + 0] = int (math.floor (r * 255 + 0.5))
                buf[idx + 1] = int (math.floor (g * 255 + 0.5))
                buf[idx + 2] = int (math.floor (b * 255 + 0.5))
                buf[idx + 3] = a
                idx += 4

        source = cairocffi.ImageSurface.create_for_data (
            memoryview (buf), cairocffi.FORMAT_ARGB32, width, height, stride
        )

        cr.save ()
        cr.set_source_surface (source, 0, 0)
        cr.paint ()
        fg_color = self.get_style_context ().get_color (Gtk.StateFlags.NORMAL)
        cr.set_line_width (1)
        cr.new_path ()
        cr.set_source_rgba (*list (fg_color))

        cr.arc (center_x, center_y, (self.size - 4) / 2. - self.ring_width,
                0, 2 * numpy.pi)
        cr.stroke ()

        cr.arc (center_x, center_y, (self.size - 2) / 2, 0, 2 * numpy.pi)
        cr.stroke ()

        cr.restore ()

        self.__draw_sector (cr, center_x, center_y)

        return False

    @property
    def histogram (self: 'HueSatWheelWidget') -> List[float]:
        return self.__hist

    @histogram.setter
    def histogram (self: 'HueSatWheelWidget', value: List[float]) -> None:
        self.__hist = value
