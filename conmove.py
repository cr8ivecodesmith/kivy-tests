import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.widget import Widget

from console import Console


SCREEN_SIZE = (80, 50)


class Con(Console):
    _sprites = []

    @property
    def last_vertice_group_idx(self):
        return (len(self._vertices)) - (4 * self._vsize)

    def set_vertice_pos(self, idx, pos, is_bg=False):
        font_w, font_h = self.font_size
        tx, ty = pos

        w, h = font_w * 0.5, font_h * 0.5
        x, y = (tx * font_w) + w, (ty * font_h) + h

        if is_bg:
            x, y = tx * font_w, ty * font_h

        self._vertices[idx:idx + 2] = (x, y)

    def add_sprite(self, sprite):
        sprite.console = self
        self.put_char(sprite.char, pos=(sprite.x, sprite.y),
                      color=sprite.color)
        sprite.base_idx = self.last_vertice_group_idx
        self._sprites.append(sprite)

    def get_sprite(self, sprite_id):
        for s in iter(self._sprites):
            if s.id == sprite_id:
                return s

    def flush(self):
        for spr in iter(self._sprites):
            spr.update()
        super().flush()


class Sprite(object):
    base_idx = 0

    def __init__(self, id, char, x, y, color=None, console=None):
        self.id = id
        self.char = char
        self.x, self.y = x, y
        self.color = color

        self.console = console

    def update(self):
        max_r = self.base_idx + (4 * self.console._vsize)
        for i in range(self.base_idx, max_r, self.console._vsize):
            self.console.set_vertice_pos(i, (self.x, self.y))


class ConEmu(Widget):
    def initialize(self):
        self.add_widget(Con(
            id='con',
            screen_size=SCREEN_SIZE,
            bg_color=(0.2, 0.2, 0.2),
        ))
        self.con = self.get_widget_by_id('con')
        self.con.add_sprite(Sprite(
            id='player',
            char='@',
            color=(1.0, 1.0, 0.0),
            x=SCREEN_SIZE[0] / 2,
            y=SCREEN_SIZE[1] / 2,
        ))
        self.con.add_sprite(Sprite(
            id='npc',
            char='@',
            x=SCREEN_SIZE[0] / 2,
            y=SCREEN_SIZE[1] / 2,
        ))
        self.player = self.con.get_sprite('player')

    def get_widget_by_id(self, widget_id, restrict=True, loopback=False):
        for obj in self.walk(restrict=restrict, loopback=loopback):
            if obj.id == widget_id:
                return obj


class ConEmuApp(App):
    def build(self):
        EventLoop.ensure_window()
        return ConEmu()

    def on_start(self):
        self.root.initialize()
        self.root.player.x += 5
        self.root.con.flush()


def main():
    ConEmuApp().run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
