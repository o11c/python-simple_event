# Copyright © 2013, Ben Longbons <b.r.longbons@gmail.com>

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import datetime
import os

from .priority_queue import PriorityQueue
from .sock_ev import best_socket_event_impl
from . import constants

class EventSet:
    ''' An EventSet is a set of callbacks that will happen when either
        a certain amount of time has passed or when a socket calls out.

        Note: there is no way to iterate over the list of fds. After all,
        some fds may be used internally, or appear/disappear unpredictably.

        Note: the ONLY way to express disinterest in an fd is
        if the callback returns CALLBACK_REMOVE. But you can set a new
        callback if you really need to, and call shutdown() to force it.

        Note: all datetimes are in UTC.
    '''
    __slots__ = ('_read', '_write', '_poll', '_timer', '_now', '_magic')

    def __init__(self):
        self._read = {}
        self._write = {}
        self._poll = best_socket_event_impl()
        self._timer = PriorityQueue()
        self._now = datetime.datetime.utcnow()
        self._magic = None # later a set


    def now(self):
        ''' Return the current logical time, which may be slightly earlier
            than the current time UTC.

            In the interest of fairness, this is only updated:
            1. on construction,
            2. during poll_timers()
            3. halfway through poll_fds()
        '''
        return self._now

    def on_timer(self, when, cb):
        ''' Schedule an event to happen after a certain amount of time.

            when is either a datetime.datetime or datetime.timedelta.
            cb is a function object that will be executed later.
            cb will take two arguments: this EventSet, and the when.
        '''
        if isinstance(when, datetime.timedelta):
            when = self.now() + when
        assert isinstance(when, datetime.datetime)
        self._timer.push(when, cb)

    def poll_timers(self):
        ''' Run timers scheduled for all times before now.

            Return the delta until the next event, or None.
        '''
        # Note: it is of utmost importance that this method does not block.
        # If you do not understand this, do NOT touch *any* event code.
        self._now = datetime.datetime.utcnow()
        while self._timer.has(self._now):
            when, callback = self._timer.pop()
            when = callback(self, when)
            if when is not None:
                self.on_timer(when, callback)

        if self._timer:
            return self._timer.peek().key - self._now
        return None

    def on_readable(self, fd, cb):
        ''' Set up a can-read event on the socket.

            The callback MUST NOT block if given a spurious event.

            cb takes two arguments, the EventSet and the fd, and returns
            either CALLBACK_PRESERVE or CALLBACK_REMOVE from constants.

            This is typically called once per fd, right after the fd
            is created, and should usually return CALLBACK_PRESERVE
            even if the callback *is* replaced.
        '''
        if fd not in self._read:
            self._poll.on_read(fd, fd in self._write)
        self._read[fd] = cb

    def on_writable(self, fd, cb):
        ''' Set up a can-write event on the socket.

            The callback MUST NOT block if given a spurious event.

            cb takes two arguments, the EventSet and the fd, and returns
            either CALLBACK_PRESERVE or CALLBACK_REMOVE from constants.

            This is typically called many times, since it does
            CALLBACK_REMOVE when the write is full.
        '''
        if fd not in self._write:
            self._poll.on_write(fd, fd in self._read)
        self._write[fd] = cb
        if self._magic is not None: # poll vs timer
            self._magic.add(fd)

    def poll_fds(self, timeout):
        ''' Check all sockets for events and execute their callbacks.

            timeout must be an instance of datetime.timedelta or None.
        '''

        # The "typical" case is: a read event happens on a socket, then
        # the callback schedules writes for it. The actual poll might
        # have happened when it was not scheduled.
        r, w = self._poll.check(timeout)
        self._now = datetime.datetime.utcnow()
        self._magic = set()

        for fd in r:
            callback = self._read[fd]
            status = callback(self, fd)
            if status is constants.CALLBACK_PRESERVE: # typical
                # note: the callback *may* have been changed. I don't care.
                continue
            assert status is constants.CALLBACK_REMOVE
            self._poll.off_read(fd, fd in self._write)
            del self._read[fd]

        w.update(self._magic) # must accept spurious

        for fd in w:
            callback = self._write[fd]
            status = callback(self, fd)
            if status is constants.CALLBACK_REMOVE: # typical
                self._poll.off_write(fd, fd in self._read)
                del self._write[fd]
                continue
            assert status is constants.CALLBACK_PRESERVE

        self._magic = None

    def run_forever(self):
        ''' Run until there is nothing to be done.

            You should call this as soon as you're done setting up
            the initial sockets (and possibly timers).
        '''
        while self._timer or self._poll:
            timeout = self.poll_timers()
            self.poll_fds(timeout)
