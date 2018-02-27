from __future__ import print_function, unicode_literals
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.internet.task import react
from twisted.python import usage
import urwid
import random

class Starfield(urwid.Widget):
    NUM_STARS = 50
    STAR_SHAPES = b"..+..++*+."
    _sizing = frozenset(["box"])
    starlines = None
    places = None

    def init_starlines(self, maxcol, maxrow):
        self.starlines = [[b" "]*maxcol for i in range(maxrow)] # base[row][col]

    def place_stars(self, maxcol, maxrow):
        self.places = [(random.randrange(0, maxcol),
                        random.randrange(0, maxrow),
                        random.randrange(0, len(self.STAR_SHAPES)),
                        ) for i in range(self.NUM_STARS)]

    def render_stars(self):
        for (col, row, shape) in self.places:
            self.starlines[row][col] = self.STAR_SHAPES[shape:shape+1]

    def twinkle_stars(self):
        self.places = [(col, row, (shape+1)%len(self.STAR_SHAPES))
                       for (col, row, shape) in self.places]
        self.render_stars()
        self._invalidate()

    def render(self, size, focus=False):
        (maxcol, maxrow) = size
        if self.starlines is None:
            self.init_starlines(maxcol, maxrow)
            self.place_stars(maxcol, maxrow)
        return urwid.TextCanvas([b"".join(whole_row)
                                 for whole_row in self.starlines],
                                maxcol=maxcol)

class TUI(object):
    def go(self):
        # returns a Deferred that fires when the GUI says quit
        done_d = Deferred()

        stars = Starfield()
        txt = urwid.Text("Hello world")
        top_status = urwid.Text("Magic-Wormhole status: closed")
        bottom_status = urwid.Text("Enter Wormhole Code: 4-pur")
        top = urwid.Frame(stars,
                          header=top_status,
                          footer=bottom_status,
                          )
        #top = urwid.Filler(pile, valign="top")
        def show_or_exit(key):
            if key.lower() == "q":
                done_d.callback(None)
                raise urwid.ExitMainLoop()
            txt.set_text(repr(key))
        evl = urwid.TwistedEventLoop(manage_reactor=False)
        loop = urwid.MainLoop(top,
                              event_loop=evl,
                              unhandled_input=show_or_exit)
        def animate(loop=None, user_data=None):
            #with open("/tmp/starbug", "a") as f:
            #    import time
            #    f.write("more {}\n".format(time.time()))
            stars.twinkle_stars()
            loop.set_alarm_in(0.3, animate)
        alarm = loop.set_alarm_in(0.2, animate)
        loop.start()

        done_d.addCallback(lambda res: loop.stop())
        return done_d

@inlineCallbacks
def open(reactor, options):
    d = TUI().go()
    yield d
    print("open exiting")


class Options(usage.Options):
    pass

def run():
    options = Options()
    options.parseOptions()
    return react(open, (options,))

