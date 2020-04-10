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
    if ELASTIC_PKGS:
        set_flag('elastic.pkgs.available')
    else:
        status.blocked('elastic-base layer option for elastic-pkgs not set.')
        return


# Install/Init ops
# We have java, and know what elastic pkg to install, so lets get to it
@when('elastic.pkgs.available',
      'apt.installed.openjdk-8-jre-headless')
@when_not('elastic.pkgs.available')
def install_elastic_pkgs():
    """Check for container, install elastic pkgs..
    """
    # Workaround for container installs is to set
    # ES_SKIP_SET_KERNEL_PARAMETERS if in container
    # so kernel files will not need to be modified on
    # elasticsearch install. See
    # https://github.com/elastic/elasticsearch/commit/32df032c5944326e351a7910a877d1992563f791
    if is_container() and ("elasticsearch" in ELASTIC_PKGS):
        os.environ['ES_SKIP_SET_KERNEL_PARAMETERS'] = 'true'
        status.maint('Installing in container based system')

    for pkg in ELASTIC_PKGS:
        status.maint(f'Installing {ELASTIC_PKG} from elastic.co apt repos')
        charms.apt.queue_install([ELASTIC_PKG])
    set_flag('elastic.pkgs.available')


@when('elastic.pkgs.available')
@when_not('elastic.base.available')
def set_elastic_base_available():
    status.active('{ELASTIC_PKG} installed.')
    set_flag('elastic.base.available')
