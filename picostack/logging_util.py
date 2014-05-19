import os
import logging
import textwrap
from picostack.socket_logger import LogRecordSocketReceiver


WHITE_LIST = ['picostk', 'picostack']
VERBOSITY_LEVELS = {
    1: logging.WARN,
    2: logging.INFO,
    3: logging.DEBUG,
    4: logging.NOTSET,
}
LOGGING_LEVELS = {
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}
VERBOSITY_TO_LEVELS = {
    1: 'WARN',
    2: 'INFO',
    3: 'DEBUG',
    4: 'NOTSET',
}


class Whitelist(logging.Filter):

    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)


def set_interactive_logging(verbosity_level):
    logging.basicConfig(
        level=VERBOSITY_LEVELS[verbosity_level],
        format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    for handler in logging.root.handlers:
        handler.addFilter(Whitelist(*WHITE_LIST))


def set_logging_as_socket_client():
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    socketHandler = logging.handlers.SocketHandler(
        'localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    socketHandler.addFilter(Whitelist(*WHITE_LIST))
    rootLogger.addHandler(socketHandler)


def set_logging_as_socket_server(logging_config_filename):
    logging.config.fileConfig(logging_config_filename,
                              disable_existing_loggers=False)
    # logging.basicConfig(
    #     format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    tcpserver = LogRecordSocketReceiver()
    tcpserver.serve_until_stopped()


def fork_me_socket_logging(logging_config_filename):
    # Fork me a server
    try:
        pid = os.fork()
        if pid == 0:
            # I am a child and will become a server.
            set_logging_as_socket_server(logging_config_filename)
            # Exit child and another after work is done.
            exit(0)
        else:
            # I am a parent and will emit as a client.
            set_logging_as_socket_client()
            return pid
    except OSError, exc:
        exc_errno = exc.errno
        exc_strerror = exc.strerror
        error = ExecProcessError(
            "%(error_message)s: [%(exc_errno)d] %(exc_strerror)s" %
            vars())
        raise error


def create_example_logging_config(logging_config_filename):
    '''Write default daemon logging config.'''
    with open(logging_config_filename, 'w+') as logging_config:
        logging_config.write(textwrap.dedent('''
        [loggers]
        keys=root, picostack

        [handlers]
        keys=picostackHandler, consoleHandler

        [formatters]
        keys=trivial

        [logger_root]
        level=DEBUG
        handlers=

        [logger_picostack]
        level=DEBUG
        handlers=picostackHandler
        qualname=picostack
        propagate=0

        [handler_consoleHandler]
        class=StreamHandler
        level=DEBUG
        formatter=trivial
        args=(sys.stdout,)

        [handler_picostackHandler]
        class=handlers.RotatingFileHandler
        level=DEBUG
        formatter=trivial
        args=('%(logs_path)s/picostk_daemon.log', 'w')
        maxBytes: 5242880
        backupCount: 7

        ''' % {
            'logs_path': os.path.dirname(logging_config_filename),
        }) + textwrap.dedent('''
        [formatter_trivial]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        datefmt=
        '''))
