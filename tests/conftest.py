# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Pytest fixtures.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os
import pytest
import logging
from configobj import ConfigObj
from inspect import getabsfile
from enaml.qt.qt_application import QtApplication
from .util import (APP_DIR_CONFIG, APP_PREFERENCES, close_all_windows,
                   ecpy_path)

#: Global variable storing the application folder path
ECPY = ''


#: Global variable linked to the --dial-sleep cmd line option.
DIALOG_SLEEP = 0


def pytest_addoption(parser):
    """Add command line options.

    """
    parser.addoption("--dial-sleep", action='store', type=float,
                     help="Time to sleep after showing a dialog")


def pytest_configure(config):
    """Turn the --dial-sleep command line into a global variable.

    """
    s = config.getoption('--dial-sleep')
    if s is not None:
        global DIALOG_SLEEP
        DIALOG_SLEEP = s


@pytest.yield_fixture(scope='session', autouse=True)
def sys_path():
    """Detect installation path of ecpy.

    Automtically called, DOES NOT use directly. Use ecpy_path to get the path
    to the ecpy directory.

    """
    import ecpy

    # Hiding current app_directory.ini to avoid losing user choice.
    path = os.path.dirname(getabsfile(ecpy))
    pref_path = os.path.join(path, APP_PREFERENCES)
    app_dir = os.path.join(pref_path, APP_DIR_CONFIG)
    new = os.path.join(pref_path, '_' + APP_DIR_CONFIG)

    # If a hidden file exists already assume it is because previous test
    # failed and do nothing.
    if os.path.isfile(app_dir) and not os.path.isfile(new):
        os.rename(app_dir, new)

    global ECPY
    ECPY = path

    yield

    # Remove created app_directory.ini and put hold one back in place.
    app_dir = os.path.join(pref_path, APP_DIR_CONFIG)
    if os.path.isfile(app_dir):
        os.remove(app_dir)

    # Put user file back in place.
    protected = os.path.join(pref_path, '_' + APP_DIR_CONFIG)
    if os.path.isfile(protected):
        os.rename(protected, app_dir)


@pytest.yield_fixture(scope='session')
def app():
    """Make sure a QtApplication is active.

    """

    app = QtApplication.instance()
    if app is None:
        app = QtApplication()
        yield app
        app.stop()
    else:
        yield app


@pytest.yield_fixture
def windows(app):
    """Fixture making sure the app is running and closing all windows.

    """
    yield
    close_all_windows()


@pytest.fixture
def app_dir(tmpdir):
    """Fixture setting the app_directory.ini file for each test.

    """
    # Create a trash app_directory.ini file. The global fixture ensure
    # that it cannot be a user file.
    app_pref = os.path.join(ecpy_path(), APP_PREFERENCES, APP_DIR_CONFIG)
    app_dir = str(tmpdir)
    conf = ConfigObj()
    conf.filename = app_pref
    conf['app_path'] = app_dir
    conf.write()
    return app_dir


@pytest.yield_fixture
def logger(caplog):
    """Fixture returning a logger for testing and cleaning handlers afterwards.

    """
    logger = logging.getLogger('test')

    yield logger

    logger.handlers = []
