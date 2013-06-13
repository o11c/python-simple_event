import unittest

import datetime
import os
import random

from simple_event.event_set import EventSet
from simple_event import constants

class TestEventSet(unittest.TestCase):
    def test_timer(self):
        evs = EventSet()
        self.timer_payload = None
        def callback(evsa, when):
            assert evs is evsa
            self.timer_payload = when
        evs.on_timer(datetime.timedelta(days=1), callback)
        evs.poll_timers()
        assert self.timer_payload is None
        now = evs.now()
        evs.on_timer(now, callback)
        evs.poll_timers()
        assert self.timer_payload is now
        del self.timer_payload

    def test_timer_order(self):
        evs = EventSet()

        self.timer_sequence = -5
        timer_list = []
        # ugh, python's closures capture by name, late!
        class Sequencer:
            def __init__(self, test, value):
                self.test = test
                self.value = value
            def __call__(self, evs, when):
                assert self.test.timer_sequence == self.value
                self.test.timer_sequence += 1

        timer_list = list(range(-5, 1))
        random.shuffle(timer_list)
        for offset in timer_list:
            func = Sequencer(self, offset)
            evs.on_timer(datetime.timedelta(seconds=offset), func)
        evs.poll_timers()
        assert self.timer_sequence == 1
        del self.timer_sequence

    def test_forever(self):
        evs = EventSet()
        evs.run_forever()

    def test_read(self):
        evs = EventSet()
        r, w = os.pipe()
        data = b'Test message for reading.\n\0\x86Random garbage.'
        assert os.write(w, data) == len(data)
        os.close(w)

        def callback(evs, rfd):
            assert os.read(rfd, constants.BUFFER_SIZE) == data
            os.close(rfd)
            return constants.CALLBACK_REMOVE
        evs.on_readable(r, callback)
        evs.run_forever()

    def test_write(self):
        evs = EventSet()
        r, w = os.pipe()
        data = b'Test message for writing.\n\0\x86Random garbage.'
        def callback(evs, wfd):
            assert os.write(wfd, data) == len(data)
            os.close(wfd)
            return constants.CALLBACK_REMOVE
        evs.on_writable(w, callback)
        evs.run_forever()
        assert os.read(r, constants.BUFFER_SIZE) == data
        os.close(r)

if __name__ == '__main__':
    unittest.main()