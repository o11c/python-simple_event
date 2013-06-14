import errno
import socket
import sys

from simple_event import constants
from simple_event.event_set import EventSet

class Echo:
    def __init__(self):
        self.buffer = bytearray()

    def reader(self, evs, fd):
        while True:
            try:
                buf = fd.recv(constants.BUFFER_SIZE)
            except socket.error as e:
                if e.errno == errno.EAGAIN:
                    return constants.CALLBACK_PRESERVE
                raise
            else:
                if not buf:
                    return constants.CALLBACK_REMOVE
                self.buffer += buf
                evs.on_writable(fd, self.writer)

    def writer(self, evs, fd):
        while self.buffer:
            try:
                n = fd.send(self.buffer)
            except socket.error as e:
                if e.errno == errno.EAGAIN:
                    return constants.CALLBACK_PRESERVE
                raise
            else:
                del self.buffer[:n]
        return constants.CALLBACK_REMOVE

def create_listen_socket(port):
    lfd = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    lfd.setblocking(False)
    # TODO: check v6only
    lfd.bind(('::', port, 0, 0))
    lfd.listen(socket.SOMAXCONN)
    return lfd

def accept_handler(evs, lfd):
    while True:
        try:
            cfd, peername = lfd.accept()
        except socket.error as e:
            if e.errno == errno.EAGAIN:
                return constants.CALLBACK_PRESERVE
            raise
        else:
            cfd.setblocking(False)
            evs.on_readable(cfd, Echo().reader)

def do_server(port):
    evs = EventSet()
    evs.on_readable(create_listen_socket(port), accept_handler)
    evs.run_forever()

def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: echo.py <portnumber>')
    try:
        port = int(sys.argv[1])
    except ValueError:
        sys.exit('Port not an integer')
    else:
        if 0 < port < 65536:
            do_server(port)
        else:
            sys.exit('Porg number not in range')

if __name__ == '__main__':
    main()
