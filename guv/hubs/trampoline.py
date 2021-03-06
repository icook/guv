import greenlet

from .hub import get_hub
from ..timeout import Timeout


def trampoline(fd, evtype, timeout=None, timeout_exc=Timeout):
    """Jump from the current greenlet to the hub and wait until the given file descriptor is ready
    for I/O, or the specified timeout elapses

    If the specified `timeout` elapses before the socket is ready to read or write, `timeout_exc`
    will be raised instead of `trampoline()` returning normally.

    When the specified file descriptor is ready for I/O, the hub internally calls the callback to
    switch back to the current (this) greenlet.

    Conditions:

    - must not be called from the hub greenlet (can be called from any other greenlet)
    - `mode` must be either READ or WRITE (not possible to watch for both simultaneously)

    :param int fd: file descriptor
    :param int evtype: either the constant READ or WRITE
    :param float timeout: (optional) maximum time to wait in seconds
    :param Exception timeout_exc: (optional) timeout Exception class

    .. note :: |internal|
    """
    #: :type: AbstractHub
    hub = get_hub()
    current = greenlet.getcurrent()

    assert hub is not current, 'do not call blocking functions from the mainloop'
    assert isinstance(fd, int)

    timer = None
    if timeout is not None:
        def _timeout(exc):
            # timeout has passed
            current.throw(exc)

        timer = hub.schedule_call_global(timeout, _timeout, timeout_exc)

    try:
        # add a watcher for this file descriptor
        listener = hub.add(evtype, fd, current.switch, current.throw)

        # switch to the hub
        try:
            return hub.switch()
        finally:
            # log.debug('(trampoline finally) remove listener for fd: {}'.format(fd))
            hub.remove(listener)
    finally:
        if timer is not None:
            timer.cancel()


def gyield():
    """Yield to other greenlets

    This is a cooperative yield which suspends the current greenlet and allows other greenlets to
    run. The current greenlet is resumed at the beginning of the next event loop iteration.
    """
    current = greenlet.getcurrent()
    hub = get_hub()
    hub.schedule_call_now(current.switch)
    hub.switch()
