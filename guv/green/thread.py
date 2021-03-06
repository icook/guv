"""Greenified _thread
"""
import greenlet
import _thread as _thread_orig

from .. import greenthread
from ..semaphore import Semaphore as LockType

__patched__ = ['get_ident', 'start_new_thread', 'start_new', 'allocate_lock',
               'allocate', 'exit', 'interrupt_main', 'stack_size', '_local',
               'LockType', '_count']

error = _thread_orig.error
__threadcount = 0


def _count():
    return __threadcount


def get_ident(gr=None):
    if gr is None:
        return id(greenlet.getcurrent())
    else:
        return id(gr)


def __thread_body(func, args, kwargs):
    global __threadcount
    __threadcount += 1
    try:
        func(*args, **kwargs)
    finally:
        __threadcount -= 1


def start_new_thread(function, args=(), kwargs=None):
    kwargs = kwargs or {}
    g = greenthread.spawn_n(__thread_body, function, args, kwargs)
    return get_ident(g)


start_new = start_new_thread


def allocate_lock(*a):
    return LockType(1)


allocate = allocate_lock


def exit():
    raise greenlet.GreenletExit


exit_thread = _thread_orig.exit_thread


def interrupt_main():
    curr = greenlet.getcurrent()
    if curr.parent and not curr.parent.dead:
        curr.parent.throw(KeyboardInterrupt())
    else:
        raise KeyboardInterrupt()


if hasattr(_thread_orig, 'stack_size'):
    __original_stack_size__ = _thread_orig.stack_size

    def stack_size(size=None):
        if size is None:
            return __original_stack_size__()
        if size > __original_stack_size__():
            return __original_stack_size__(size)
        else:
            pass
            # not going to decrease stack_size, because otherwise other greenlets in
            # this thread will suffer
