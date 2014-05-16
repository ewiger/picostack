import ConfigParser
import os
import time
import logging
from picostack.vm_manager import VmManager


logger = logging.getLogger(__name__)
USER_HOME_DIR = os.path.expanduser('~/')


class PicoStackApp(object):
    '''
    To understand implementation details see DaemonRunner from
    daemoncxt.runner in https://github.com/ewiger/daemoncxt
    '''

    def __init__(self, name, config_vars, debug=False,
                 is_interactive=False, logger=None):
        self.name = name
        self.config_name = config_vars['config_name']
        self.manager_name = config_vars['manager_name']
        self.debug = debug
        self.is_interactive = is_interactive
        self.config = ConfigParser.ConfigParser(defaults=config_vars)
        self.init_config()
        self.vm_manager = VmManager.create(self.manager_name, self.config)

    def init_config(self):
        # Start with building some defaults.
        # Init/set application options.
        self.config.add_section('app')
        self.config.set('app', 'statepath', '%(default_statepath)s')
        self.config.set('app', 'vm_manager', '%(manager_name)s')
        self.config.set('app', 'is_interactive',
                        str(int(self.is_interactive)))
        self.config.set('app', 'log_path',
                        '%(default_statepath)s/logs')
        self.config.set('app', 'pidfiles_path',
                        '%(default_statepath)s/pidfiles')
        self.config.set('app', 'first_mapped_port',
                        '10000')
        self.config.set('app', 'last_mapped_port',
                        '10100')
        self.config.set('app', 'logging_config_path',
                        '%(default_statepath)s/logging.conf')
        # Init/set dameon options.
        self.config.add_section('daemon')
        self.config.set('daemon', 'stdin_path', '/dev/null')
        self.config.set('daemon', 'stdout_path',
                        '/dev/tty' if self.debug else '/dev/null')
        self.config.set('daemon', 'stderr_path',
                        '/dev/tty' if self.debug else '/dev/null')
        self.config.set('daemon', 'pidfile_path',
                        '%(default_statepath)s/' + self.name + '.pid')
        self.config.set('daemon', 'pidfile_timeout', '5')
        self.config.set('daemon', 'sleeping_pause', '10')
        # Init/set VM manager options.
        self.config.add_section('vm_manager')
        self.config.set('vm_manager', 'vm_image_path',
                        '%(default_statepath)s/images')
        self.config.set('vm_manager', 'vm_disk_path',
                        '%(default_statepath)s/disks')

    def load_config_file(self, config_name, config_dir):
        '''
        Load configuration from supplied filename. By default configuration
        directory is set to point to '.../bin/<APP>.conf'
        '''
        config_path = os.path.join(config_dir, config_name)
        if os.path.exists(config_path):
            logger.info('Loading %s' % config_path)
            self.config.read(config_path)

    def load_config(self, config_dir, config_name=None):
        '''Load more configuration from default locations'''
        if config_name is None:
            config_name = self.config_name
        # Load defaults from config dir, i.e. ~/.picostack.
        self.load_config_file(config_name, config_dir)
        # Override with user config.
        self.load_config_file(config_name, USER_HOME_DIR)

    def validate_config(self):
        '''(Optional) validate config for arguments'''
        # First run optional (method can be empty) config check for VM manager
        # components.
        self.vm_manager.validate_config()
        # Assert configuration for correctness.
        assert self.config.has_section('app')
        assert self.config.get('app', 'statepath') is not None
        assert os.path.exists(self.config.get('app', 'log_path'))
        assert os.path.exists(self.config.get('app', 'pidfiles_path'))
        assert os.path.exists(self.config.get('app', 'logging_config_path'))

    @property
    def state_path(self):
        if self.__state_path is None:
            # Try to get configuration option.
            self.__state_path = self.config.get('app', 'statepath')
            if not os.path.exists(self.__state_path):
                logger.warn('Creating a missing dir: %s' % self.__state_path)
                os.makedirs(self.__state_path)
        return self.__state_path

    @property
    def stdin_path(self):
        '''Part of DaemonRunner protocol'''
        return self.config.get('daemon', 'stdin_path')

    @property
    def stdout_path(self):
        '''Part of DaemonRunner protocol'''
        return self.config.get('daemon', 'stdout_path')

    @property
    def stderr_path(self):
        '''Part of DaemonRunner protocol'''
        return self.config.get('daemon', 'stderr_path')

    @property
    def pidfile_path(self):
        '''Part of DaemonRunner protocol'''
        return self.config.get('daemon', 'pidfile_path')

    @property
    def pidfile_timeout(self):
        '''Part of DaemonRunner protocol'''
        return self.config.getint('daemon', 'pidfile_timeout')

    def step(self):
        '''A single step of actual work, done by daemon'''
        self.vm_manager.build_machines()
        self.vm_manager.start_machines()
        self.vm_manager.stop_machines()
        self.vm_manager.destory_machines()

    def run(self):
        while True:
            self.step()
            # Sleep x seconds.
            sleeping_pause = self.config.getint('daemon', 'sleeping_pause')
            logger.info('Sleeping for %d (sec)..' % sleeping_pause)
            time.sleep(sleeping_pause)


def get_picostack_app(app_name, config_vars, config_dir,
                      is_interactive, is_debug, only_defaults=False):
    picostack_app = PicoStackApp(app_name,
                                 config_vars,
                                 is_interactive=is_interactive,
                                 debug=is_debug,
                                 logger=logger)
    if only_defaults:
        return picostack_app
    picostack_app.load_config(config_dir)
    picostack_app.validate_config()
    return picostack_app
