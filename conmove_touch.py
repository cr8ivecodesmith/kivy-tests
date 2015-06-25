import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window, Keyboard
from kivy.uix.widget import Widget
from kivy.vector import Vector

from console import Console


SCREEN_SIZE = (100, 50)


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
        # NOTES: Optimization idea:
        # - delete or manipulate only indices since they're the ones that
        #   controls ordering.
        del self._vertices[self._vsize * 4:]
        del self._indices[6:]


class Sprite(object):
    def __init__(self, char, x, y, id=None, color=None, console=None):
        self.id = id
        self.char = char
        self.x, self.y = x, y
        self.color = color
        self.console = console

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


class ConEmu(Widget):
    def initialize(self):
        Window.bind(on_key_down=self.on_key_down)
        self.touch_console_pos = (0, 0)
        self.touch_info = {}

        self.add_widget(Con(
            id='con',
            screen_size=SCREEN_SIZE,
            bg_color=(0.3, 0.3, 0.3),
        ))
        self.con = self.get_widget_by_id('con')
        self.con.add_sprite(Sprite(
            id='player',
            char='@',
            color=(1.0, 1.0, 0.0),
            x=SCREEN_SIZE[0] / 2,
            y=SCREEN_SIZE[1] / 2,
        ))
        self.player = self.con.get_sprite('player')

    def on_touch_up(self, touch):
        # Debug section
        self.touch_console_pos = self.con.get_console_pos((touch.x, touch.y))
        self.touch_info['pos'] = touch.pos
        self.touch_info['time_start'] = touch.time_start
        self.touch_info['time_update'] = touch.time_update
        self.touch_info['time_end'] = touch.time_end
        self.touch_info['triple_tap_time'] = touch.triple_tap_time
        self.touch_info['double_tap_time'] = touch.double_tap_time

        # Start of move code
        vec = Vector(touch.pos) - Vector(touch.opos)

        # If travel distance is short then it's probably a tap or click.
        if vec.length() < 50:
            return

        dx, dy = vec.normalize()
        self.player.move(round(dx), round(dy))
        self.update()

    def update(self, nap=0.0):
        self.con.put_text('nap: {}'.format(nap), pos=(1, 1))
        self.con.put_text('screen size: {}'.format(
            SCREEN_SIZE), pos=(1, 2))

        self.con.put_text('touch console pos: {}'.format(
            self.touch_console_pos), pos=(1, 4))
        self.con.put_text('player coord: ({}, {})'.format(
            self.player.x, self.player.y), pos=(1, 5))

        self.con.put_text('touch pixel pos: ({:.4f}, {:.4f})'.format(
            self.touch_info.get('pos', (0, 0))[0],
            self.touch_info.get('pos', (0, 0))[1]), pos=(1, 7))
        self.con.put_text('player pixel pos: {}'.format(
            self.con.get_pixel_pos((self.player.x, self.player.y))),
            pos=(1, 8))

        self.con.put_text('touch time update: {}'.format(
            self.touch_info.get('time_update')), pos=(SCREEN_SIZE[0] / 2, 2))
        self.con.put_text('touch time end: {}'.format(
            self.touch_info.get('time_end')), pos=(SCREEN_SIZE[0] / 2, 3))
        self.con.put_text('touch time start: {}'.format(
            self.touch_info.get('time_start')), pos=(SCREEN_SIZE[0] / 2, 4))

        self.con.put_text('touch double tap time: {}'.format(
            self.touch_info.get('double_tap_time')),
            pos=(SCREEN_SIZE[0] / 2, 6))
        self.con.put_text('touch triple tap time: {}'.format(
            self.touch_info.get('triple_tap_time')),
            pos=(SCREEN_SIZE[0] / 2, 7))

        self.con.flush()

    def get_widget_by_id(self, widget_id, restrict=True, loopback=False):
        for obj in self.walk(restrict=restrict, loopback=loopback):
            if obj.id == widget_id:
                return obj

    def on_key_down(self, window, key, *args):
        code = Keyboard.keycodes

        if code['h'] == key or code['left'] == key:
            self.player.move(-1, 0)
        elif code['l'] == key or code['right'] == key:
            self.player.move(1, 0)
        elif code['k'] == key or code['up'] == key:
            self.player.move(0, 1)
        elif code['j'] == key or code['down'] == key:
            self.player.move(0, -1)
        elif code['y'] == key:
            self.player.move(-1, 1)
        elif code['b'] == key:
            self.player.move(-1, -1)
        elif code['u'] == key:
            self.player.move(1, 1)
        elif code['n'] == key:
            self.player.move(1, -1)

        self.update()


class ConEmuApp(App):
    def build(self):
        EventLoop.ensure_window()
        return ConEmu()

    def on_start(self):
        self.root.initialize()
        self.root.update()
        # Clock.schedule_interval(self.root.update, 1 / 25.0)


def main():
    ConEmuApp().run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
