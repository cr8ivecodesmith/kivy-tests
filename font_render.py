import kivy
kivy.require('1.9.0')

import itertools
from collections import namedtuple

from kivy.app import App
from kivy.base import EventLoop
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


def load_font(font_file, font_size):
    """ Returns the font as a texture and a mapping of its values.

    """
    image = Image(font_file)
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


class FontRender(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.source = 'font_render.glsl'

        self.scale = 1.0
        self.font_size = (8, 12)
        self.texture, self.uvmap = load_font('terminal8x12_gs_ro.png',
                                             self.font_size)

        self.vfmt = (
            (b'vCenter', 2, 'float'),
            (b'vScale', 1, 'float'),
            (b'vPosition', 2, 'float'),
            (b'vTexCoords0', 2, 'float'),
            (b'vColor', 3, 'float'),
        )

    def render(self):
        ff_vertices, ff_indices = self.render_font_file()
        msg_vertices, msg_indices = self.render_text(
            'Awesome font rendering from a sprite sheet! ;)',
            pos=(5, 200),
            color=(0.5, 1.0, 1.0))
        msg2_vertices, msg2_indices = self.render_text(
            'Demonstration of background clipping for transparency.',
            pos=(5, 150),
            color=(0.5, 1.0, 1.0))

        with self.canvas:
            Mesh(fmt=self.vfmt, mode='triangles',
                 indices=ff_indices, vertices=ff_vertices,
                 texture=self.texture)
            Mesh(fmt=self.vfmt, mode='triangles',
                 indices=msg_indices, vertices=msg_vertices,
                 texture=self.texture)
            Mesh(fmt=self.vfmt, mode='triangles',
                 indices=msg2_indices, vertices=msg2_vertices,
                 texture=self.texture)

    def render_font_file(self, color=None, scale=None):
        r, g, b = color or (1.0, 1.0, 1.0)
        scale = scale or self.scale
        tex_w, tex_h = self.texture.size

        vertices = [
            0, 0, scale, 0, 0, 0, 1, r, g, b,
            0, 0, scale, tex_w, 0, 1, 1, r, g, b,
            0, 0, scale, tex_w, tex_h, 1, 0, r, g, b,
            0, 0, scale, 0, tex_h, 0, 0, r, g, b,
        ]

        indices = [
            0, 1, 2,
            2, 3, 0
        ]

        return vertices, indices

    def render_text(self, text, pos, color=None):
        _color = (1.0, 1.0, 1.0)

        r, g, b = color or _color
        font_w, font_h = self.font_size
        x, y = pos

        vertices = []
        indices = []
        for idx, char in enumerate(text):
            uv = self.uvmap.get(ord(char)) or self.uvmap.get(ord(' '))
            j = 4 * idx

            vertices.extend((
                x, y, self.scale, -uv.su, -uv.sv, uv.u0, uv.v1, r, g, b,
                x, y, self.scale, uv.su, -uv.sv, uv.u1, uv.v1, r, g, b,
                x, y, self.scale, uv.su, uv.sv, uv.u1, uv.v0, r, g, b,
                x, y, self.scale, -uv.su, uv.sv, uv.u0, uv.v0, r, g, b,
            ))
            indices.extend((
                j, j + 1, j + 2,
                j + 2, j + 3, j
            ))

            x += font_w

        return vertices, indices


class FontRenderApp(App):
    def build(self):
        EventLoop.ensure_window()
        return FontRender()

    def on_start(self):
        self.root.render()


def main():
    FontRenderApp().run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
