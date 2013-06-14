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

import select

def fileno(fd):
    ''' While select.select() preserves actual socket objects passed,
        select.poll and select.epoll will always return the integer.

        This is used to turn an integer or socket into an integer,
        to be used in a map key.
    '''
    if isinstance(fd, int):
        return fd
    return fd.fileno()

SelectImpl = None
PollImpl = None

class EpollImpl:
    __slots__ = ('_impl', '_map')

    def __init__(self):
        self._impl = select.epoll()
        self._map = {}

    def __bool__(self):
        return bool(self._map)

    def on_read(self, fd, also_write):
        ''' Be interested in readability of this fd.
        '''
        if also_write:
            self._impl.modify(fd, select.EPOLLIN | select.EPOLLOUT)
        else:
            self._impl.register(fd, select.EPOLLIN)
            self._map[fileno(fd)] = fd

    def on_write(self, fd, also_read):
        ''' Be interested in writability of this fd.
        '''
        if also_read:
            self._impl.modify(fd, select.EPOLLIN | select.EPOLLOUT)
        else:
            self._impl.register(fd, select.EPOLLOUT)
            self._map[fileno(fd)] = fd

    def off_read(self, fd, still_write):
        ''' Be disinterested in readability of this fd.
        '''
        if still_write:
            self._impl.modify(fd, select.EPOLLOUT)
        else:
            self._impl.unregister(fd)
            del self._map[fileno(fd)]

    def off_write(self, fd, still_read):
        ''' Be disinterested in readability of this fd.
        '''
        if still_read:
            self._impl.modify(fd, select.EPOLLIN)
        else:
            self._impl.unregister(fd)
            del self._map[fileno(fd)]

    def check(self, timeout):
        ''' return a tuple (r, w) of sets of fds ready for IO.
        '''
        if timeout is None:
            result = self._impl.poll()
        else:
            result = self._impl.poll(timeout.total_seconds())

        r = set()
        w = set()
        for fd, events in result:
            fd = self._map[fd]
            if events & select.EPOLLIN:
                r.add(fd)
            if events & select.EPOLLOUT:
                w.add(fd)
        return r, w

def best_socket_event_impl():
    try:
        return EpollImpl()
    except AttributeError:
        try:
            return PollImpl()
        except AttributeError:
            return SelectImpl()
