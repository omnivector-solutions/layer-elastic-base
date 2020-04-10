#!/usr/local/sbin/charm-env python
# pylint: disable=c0111,c0103,c0301
import os
import subprocess as sp

from charms.layer import options

from charms.reactive import (
    set_flag,
    when,
    when_not,
)

from charmhelpers.core.host import is_container

from charms.layer import status

import charms.apt


ELASTIC_PKGS = options.get('elastic-base', 'elastic-pkgs')


@when_not('elastic.pkgs.available')
def check_elastic_pkg_layer_option():
    if len(ELASTIC_PKGS) > 0:
        set_flag('elastic.pkgs.available')
    else:
        status.blocked('elastic-base layer option for elastic-pkgs not set.')
        return


# Install/Init ops
# We have java, and know what elastic pkg to install, so lets get to it
@when('elastic.pkgs.available',
      'apt.installed.openjdk-8-jre-headless')
@when_not('elastic.pkgs.installed')
def install_elastic_pkgs():
    for pkg in ELASTIC_PKGS:
        status.maint(f'Installing {pkg} from elastic.co apt repos')
        charms.apt.queue_install([pkg])
    set_flag('elastic.pkgs.installed')


@when('elastic.pkgs.installed')
@when_not('elastic.base.available')
def set_elastic_base_available():
    set_flag('elastic.base.available')
