import kivy
kivy.require('1.9.0')

import pdb
import itertools
from collections import namedtuple

from kivy.core.image import Image
from kivy.graphics import Mesh
from kivy.graphics.instructions import RenderContext
from kivy.uix.widget import Widget


UVMapping = namedtuple('UVMapping', 'u0 v0 u1 v1 su sv')
""" Universal value holder for sprites

This follows the standard OpenGL vertex mapping where 0,0 is at the top-left.

u0, v0 - Coords of the sprite's top-left corner
u1, v1 - Coords of the sprite's bottom-right corner
su - Sprite width divided by 2; useful when building array of vertices
sv - Sprite height divided by 2

"""


def load_font(font_source, font_size):
    """ Returns the font as a texture and a mapping of its values.

    """
    image = Image(font_source)
    tex_w, tex_h = image.size
    font_w, font_h = font_size

    uvmap = {}
    char_ord = 0
    range_x = range(0, tex_w, font_w)
    range_y = range(0, tex_h, font_h)
    for y0, x0 in itertools.product(range_y, range_x):
        x1, y1 = x0 + font_w, y0 + font_h
        uvmap[char_ord] = UVMapping(
            x0 / tex_w, y0 / tex_h,
            x1 / tex_w, y1 / tex_h,
            font_w * 0.5, font_h * 0.5,
        )
        char_ord += 1

    return image.texture, uvmap


class Console(Widget):
    _vertices = []
    _indices = []
    _vfmt = (
        (b'vCenter', 2, 'float'),
        (b'vPosition', 2, 'float'),
        (b'vTexCoords0', 2, 'float'),
        (b'vColor', 3, 'float'),
        (b'isTexFlag', 1, 'float'),
    )
    _vsize = sum(i[1] for i in _vfmt)
    _fg_color = (1.0, 1.0, 1.0)
    _bg_color = (0.0, 0.0, 0.0)
    _shader = 'console.glsl'
    _font_source = 'terminal8x12_gs_ro.png'
    _font_size = (8, 12)

    def __init__(self, screen_size, font_source=None, font_size=None,
                 fg_color=None, bg_color=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.screen_size = screen_size
        self.fg_color = fg_color or self._fg_color
        self.bg_color = bg_color or self._bg_color
        self.font_source = font_source or self._font_source
        self.font_size = font_size or self._font_size
        self.font_tex, self.font_map = load_font(self.font_source,
                                                 self.font_size)

        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.source = self._shader
        self.console_bg_color()

    @property
    def max_indice(self):
        return max(self._indices) + 1 if self._indices else 0

    def get_pixel_pos(self, pos, is_bg=False):
        font_w, font_h = self.font_size
        tx, ty = pos
        w, h = font_w * 0.5, font_h * 0.5
        x, y = (tx * font_w) + w, (ty * font_h) + h

        if is_bg:
            x, y = tx * font_w, ty * font_h

        return x, y

    def console_bg_color(self):
        self.put_rect((0, 0), self.screen_size, self.bg_color)

    def put_char(self, char, pos, color=None):
        x, y = self.get_pixel_pos(pos)

        r, g, b = color or self.fg_color
        idx = self.max_indice
        uv = self.font_map.get(ord(char)) or self.uvmap.get(ord(' '))

        self._vertices.extend((
            x, y, -uv.su, -uv.sv, uv.u0, uv.v1, r, g, b, 1,
            x, y, uv.su, -uv.sv, uv.u1, uv.v1, r, g, b, 1,
            x, y, uv.su, uv.sv, uv.u1, uv.v0, r, g, b, 1,
            x, y, -uv.su, uv.sv, uv.u0, uv.v0, r, g, b, 1,
        ))
        self._indices.extend((
            idx, idx + 1, idx + 2,
            idx + 2, idx + 3, idx
        ))

    def put_bg_color(self, pos, color):
        font_w, font_h = self.font_size
        x, y = self.get_pixel_pos(pos, is_bg=True)

        r, g, b = color
        idx = self.max_indice

        self._vertices.extend((
            x, y, 0, 0, 0, 0, r, g, b, 0,
            x, y, font_w, 0, 0, 0, r, g, b, 0,
            x, y, font_w, font_h, 0, 0, r, g, b, 0,
            x, y, 0, font_h, 0, 0, r, g, b, 0,
        ))
        self._indices.extend((
            idx, idx + 1, idx + 2,
            idx + 2, idx + 3, idx
        ))

    def put_text(self, text, pos, color=None, wrap=None):
        x, y = pos
        start_x = x
        ctr = 0
        for char in iter(text):
            if isinstance(wrap, int) and ctr >= wrap:
                ctr = 0
                x = start_x
                y -= 1

            if not char.strip() and x == start_x:
                continue

            self.put_char(char, pos=(x, y), color=color)
            x += 1
            ctr += 1

    def put_rect(self, pos, size, color):
        font_w, font_h = self.font_size
        w, h = size
        x, y = self.get_pixel_pos(pos, is_bg=True)

        r, g, b = color
        idx = self.max_indice

        self._vertices.extend((
            x, y, 0, 0, 0, 0, r, g, b, 0,
            x, y, w * font_w, 0, 0, 0, r, g, b, 0,
            x, y, w * font_w, h * font_h, 0, 0, r, g, b, 0,
            x, y, 0, h * font_h, 0, 0, r, g, b, 0,
        ))
        self._indices.extend((
            idx, idx + 1, idx + 2,
            idx + 2, idx + 3, idx
        ))

    def flush(self):
        self.canvas.clear()
        with self.canvas:
            Mesh(fmt=self._vfmt, mode='triangles',
                 indices=self._indices, vertices=self._vertices,
                 texture=self.font_tex)
