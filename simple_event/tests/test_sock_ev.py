import unittest

from simple_event.sock_ev import SelectImpl, PollImpl, EpollImpl

# TODO put tests of the explicit implementation
# and mark with XFAILs if the system does not support poll/epoll.

if __name__ == '__main__':
    unittest.main()
