import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.base import EventLoop
from kivy.uix.widget import Widget

from console import Console


SCREEN_SIZE = (80, 50)


class ConEmu(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Console(
            id='con',
            screen_size=SCREEN_SIZE,
            bg_color=(0.3, 0.3, 0.3),
        ))

        con = self.get_widget_by_id('con')

        con.put_text('Sup world! No wrapping here.', pos=(0, 0),
                     color=(0.4, 0.8, 0.2))
        con.put_text('This is really awesome!', pos=(0, 2), wrap=14)

        con.put_bg_color(pos=(0, 4), color=(0.5, 0.7, 1.0))
        con.put_bg_color(pos=(1, 4), color=(0.4, 0.6, 1.0))
        con.put_bg_color(pos=(2, 4), color=(0.3, 0.5, 1.0))
        con.put_text('<- Lovely color tiles! :)', pos=(4, 4))

        con.put_bg_color(pos=(0, 5), color=(0.1, 0.6, 1.0))
        con.put_char('@', pos=(0, 5))
        con.put_text('<- This is char with background color.', pos=(2, 5))

        con.put_rect(pos=(0, 7), size=(20, 1), color=(0.3, 0.5, 1.0))
        con.put_rect(pos=(0, 8), size=(20, 2), color=(1.0, 0.5, 0.3))
        con.put_text('<- Bars anyone?', pos=(21, 9))

        con.flush()

    def get_widget_by_id(self, widget_id, restrict=True, loopback=False):
        for obj in self.walk(restrict=restrict, loopback=loopback):
            if obj.id == widget_id:
                return obj


class ConEmuApp(App):
    def build(self):
        EventLoop.ensure_window()
        return ConEmu()


def main():
    ConEmuApp().run()


if __name__ == '__main__':
    import sys
    sys.exit(main())
