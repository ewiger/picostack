#!/usr/bin/env python
# TODO: migrate to distribute?
#import distribute_setup
#distribute_setup.use_setuptools()


import os.path
import sys
from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


def get_version():
    src_path = os.path.join(os.path.dirname(__file__), 'picostack')
    sys.path.append(src_path)
    import picostack
    return picostack.__version__


setup(
    name='picostack',
    version=get_version(),
    description='A super lightweight KVM virtualization manager',
    long_description=readme(),
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    url='https://github.com/ewiger/picostack',
    license='MIT',
    scripts=['picostk', 'picostk-django', 'pstk'],
    packages=['picostack', 'picostack.vms'],
    include_package_data=True,
    download_url='https://github.com/ewiger/picostack/tarball/master',
    install_requires=[
        'sh >= 1.08',
        'daemoncxt >= 1.5.7',
        'Django >= 1.6.2',
        'psutil >= 2.1.1',
    ],
    data_files=[
        ('/etc/init.d', ['pstk']),
    ],
)
