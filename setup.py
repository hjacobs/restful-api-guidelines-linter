#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import os
import platform
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


def read_version(package):
    with open(os.path.join(package, '__init__.py'), 'r') as fd:
        for line in fd:
            if line.startswith('__version__ = '):
                return line.split()[-1].strip().strip("'")

version = 0.1

py_major_minor_version = tuple(int(v.rstrip('+')) for v in platform.python_version_tuple()[:2])


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    requires = [req for req in content.split('\\n') if req != '']
    if py_major_minor_version < (3, 4):
        requires.append('pathlib')
    return requires


class PyTest(TestCommand):

    user_options = [('cov-html=', None, 'Generate junit html report')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.pytest_args = ['--cov', 'linter', '--cov-report', 'term-missing', '-v']
        self.cov_html = False

    def finalize_options(self):
        TestCommand.finalize_options(self)
        if self.cov_html:
            self.pytest_args.extend(['--cov-report', 'html'])
        self.pytest_args.extend(['tests'])

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def readme():
    try:
        return open('README.rst', encoding='utf-8').read()
    except TypeError:
        return open('README.rst').read()


setup(
    name='restful-api-guidelines-linter',
    packages=find_packages(),
    version=version,
    description='',
    long_description=readme(),
    author='Zalando SE',
    url='https://github.com/zalando-incubator/restful-api-guidelines-linter',
    keywords='',
    license='',
    setup_requires=['flake8'],
    install_requires=get_install_requirements('requirements.txt'),
    tests_require=['pytest-cov', 'pytest', 'mock', 'decorator'],
    cmdclass={'test': PyTest},
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    entry_points={'console_scripts': ['restful-api-guidelines-linter = restful_api_guidelines_linter.cli:main']}
)
