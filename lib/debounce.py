# pylint: disable=too-many-arguments, too-many-instance-attributes
# source https://gist.github.com/SpotlightKid/0a0aac56606286a80f860b116423c94f
#
# inspired by: https://forum.micropython.org/viewtopic.php?t=1938#p10931

import micropython
import machine

timer_init = lambda t, p, cb: t.init(period=p, callback=cb)


class DebouncedSwitch:
    """Debounced switch"""

    def __init__(self, sw, cb, arg=None, delay=50, tid=4):
        self.sw = sw
        self._sw_cb = self.sw_cb
        self._tim_cb = self.tim_cb
        self._set_cb = getattr(self.sw, "callback", None) or self.sw.irq
        self.delay = delay
        self.tim = machine.Timer(tid)
        self.callback(cb, arg)

    def sw_cb(self, pin=None):
        self._set_cb(None)
        timer_init(self.tim, self.delay, self._tim_cb)

    def tim_cb(self, tim):
        tim.deinit()
        if self.sw():
            micropython.schedule(self.cb, self.arg)
        self._set_cb(self._sw_cb if self.cb else None)

    def callback(self, cb, arg=None):
        self.tim.deinit()
        self.cb = cb
        self.arg = arg
        self._set_cb(self._sw_cb if cb else None)
