import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window, Keyboard
from kivy.uix.widget import Widget

from console import Console


SCREEN_SIZE = (80, 50)


class Con(Console):
    _sprites = []

    def add_sprite(self, sprite):
        sprite.console = self
        self._sprites.append(sprite)

    def get_sprite(self, sprite_id):
        for spr in iter(self._sprites):
            if spr.id == sprite_id:
                return spr

    def flush(self):
        for spr in iter(self._sprites):
            self.put_char(spr.char, pos=(spr.x, spr.y),
                          color=spr.color)

        super().flush()

        # Delete everything except the background color
        del self._vertices[self._vsize * 4:]
        del self._indices[6:]


class Sprite(object):
    def __init__(self, id, char, x, y, color=None, console=None):
        self.id = id
        self.char = char
        self.x, self.y = x, y
        self.color = color
        self.console = console


class ConEmu(Widget):
    def initialize(self):
        Window.bind(on_key_down=self.on_key_down)

        self.add_widget(Con(
            id='con',
            screen_size=SCREEN_SIZE,
            bg_color=(0.3, 0.3, 0.3),
        ))
        self.con = self.get_widget_by_id('con')
        self.con.add_sprite(Sprite(
            id='npc',
            char='@',
            x=SCREEN_SIZE[0] / 2,
            y=SCREEN_SIZE[1] / 2,
        ))
        self.con.add_sprite(Sprite(
            id='player',
            char='@',
            color=(1.0, 1.0, 0.0),
            x=SCREEN_SIZE[0] / 2 + 5,
            y=SCREEN_SIZE[1] / 2,
        ))
        self.player = self.con.get_sprite('player')

    def update(self, nap):
        self.con.put_text('nap: {:.4f}'.format(nap), pos=(1, 1))
        self.con.put_text('screen size: {}'.format(
            SCREEN_SIZE), pos=(1, 2))
        self.con.put_text('player coord: ({}, {})'.format(
            self.player.x, self.player.y), pos=(1, 4))

        self.con.flush()

    def get_widget_by_id(self, widget_id, restrict=True, loopback=False):
        for obj in self.walk(restrict=restrict, loopback=loopback):
            if obj.id == widget_id:
                return obj

    def on_key_down(self, window, key, *args):
        code = Keyboard.keycodes
        if code['h'] == key or code['left'] == key:
            self.player.x -= 1
        elif code['l'] == key or code['right'] == key:
            self.player.x += 1
        elif code['k'] == key or code['up'] == key:
            self.player.y += 1
        elif code['j'] == key or code['down'] == key:
            self.player.y -= 1
        elif code['y'] == key:
            self.player.x -= 1
            self.player.y += 1
        elif code['b'] == key:
            self.player.x -= 1
            self.player.y -= 1
        elif code['u'] == key:
            self.player.x += 1
            self.player.y += 1
        elif code['n'] == key:
            self.player.x += 1
            self.player.y -= 1


class ConEmuApp(App):
    def build(self):
        EventLoop.ensure_window()
        return ConEmu()

    def on_start(self):
        self.root.initialize()
        Clock.schedule_interval(self.root.update, 1 / 25.0)


def main():
    ConEmuApp().run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
