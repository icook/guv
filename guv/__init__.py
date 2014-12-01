version_info = (0, 30, 1)
__version__ = '.'.join(map(str, version_info))

try:
    from . import greenpool
    from . import queue
    from .hubs.trampoline import gyield
    from .greenthread import sleep, spawn, spawn_n, spawn_after, kill
    from .greenpool import GreenPool, GreenPile
    from .timeout import Timeout, with_timeout
    from .patcher import import_patched, monkey_patch
    from .server import serve, listen, connect, StopServe, wrap_ssl

    import pyuv_cffi  # only to compile the shared library before monkey-patching

except ImportError as e:
    # This is to make Debian packaging easier, it ignores import errors of greenlet so that the
    # packager can still at least access the version. Also this makes easy_install a little quieter
    if 'greenlet' not in str(e):
        # any other exception should be printed
        import traceback

        traceback.print_exc()
