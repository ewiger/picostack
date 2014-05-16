import os
import logging
import textwrap


WHITE_LIST = ['picostk', 'picostack']
VERBOSITY_LEVELS = {
    0: logging.NOTSET,
    1: logging.WARN,
    2: logging.INFO,
    3: logging.DEBUG,
}
LOGGING_LEVELS = {
    'NOTSET': logging.NOTSET,
    'WARN': logging.WARN,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}
VERBOSITY_TO_LEVELS = {
    0: 'NOTSET',
    1: 'WARN',
    2: 'INFO',
    3: 'DEBUG',
}


def getBasicLogger(name, level):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(name)-20s %(levelname)-8s '
                               '%(message)s',
                        datefmt='%m-%d %H:%M')
    console = logging.StreamHandler()
    console.setLevel(level)
    logger = logging.getLogger(name)
    return logger


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


def set_filestream_logging(logging_config_filename):
    logging.config.fileConfig(logging_config_filename,
                              disable_existing_loggers=False)


def create_example_logging_config(logging_config_filename):
    '''Write default daemon logging config.'''
    with open(logging_config_filename, 'w+') as logging_config:
        logging_config.write(textwrap.dedent('''
        [loggers]
        keys=root

        [handlers]
        keys=picostackFileLogHandler,consoleHandler

        [formatters]
        keys=simpleFormatter

        [logger_root]
        level=DEBUG
        handlers=picostackFileLogHandler

        [handler_consoleHandler]
        class=StreamHandler
        level=DEBUG
        formatter=simpleFormatter
        args=(sys.stdout,)

        [handler_picostackFileLogHandler]
        class=FileHandler
        level=DEBUG
        formatter=simpleFormatter
        args=('%(logs_path)s/picostk_daemon.log', 'w')
        ''' % {
            'logs_path': os.path.dirname(logging_config_filename),
        }) + textwrap.dedent('''
        [formatter_simpleFormatter]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        datefmt=
        '''))
