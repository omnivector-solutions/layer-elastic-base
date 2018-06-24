#!/usr/local/sbin/charm-env python
# pylint: disable=c0111,c0103,c0301
import os
import subprocess as sp

from charms.layer import options

from charms.reactive import (
    set_flag,
    when,
    when_any,
    when_not,
)

from charmhelpers.core.hookenv import (
    config,
    resource_get,
    status_set,
)

from charmhelpers.core.host import is_container

import charms.apt


ELASTIC_PKG = options('elastic-base').get('elastic-pkg', '')


@when_not('elastic.pkg.set')
def check_elastic_pkg_layer_option():
    if ELASTIC_PKG:
        set_flag('elastic.pkg.set')
    else:
        status_set('blocked',
                   'elastic-base layer config for elastic-pkg not set.')


# Install/Init ops
# We have java, and know what elastic pkg to install, so lets get to it
@when('apt.installed.openjdk-8-jre-headless', 'elastic.pkg.set')
@when_not('elastic.pkg.available')
def install_elastic_pkg():
    """Check for container, install elastic pkg
    from either apt or supplied resource .deb.
    """
    # TODO(jamesbeedy): SNAP Elastic pkgs, integrate snap packaging

    # Workaround for container installs is to set
    # ES_SKIP_SET_KERNEL_PARAMETERS if in container
    # so kernel files will not need to be modified on
    # elasticsearch install. See
    # https://github.com/elastic/elasticsearch/commit/32df032c5944326e351a7910a877d1992563f791
    if is_container() and (ELASTIC_PKG == "elasticsearch"):
        os.environ['ES_SKIP_SET_KERNEL_PARAMETERS'] = 'true'
        status_set('maintenance',
                   "Installing in container based system")

    elastic_deb = resource_get('elastic-deb')
    if os.stat(elastic_deb).st_size > 0:
        status_set('maintenance',
                   "Installing {} from supplied .deb resource".format(
                       ELASTIC_PKG.capitalize()))
        sp.call(['dpkg', '-i', elastic_deb])
        set_flag('deb.installed.{}'.format(ELASTIC_PKG))
    else:
        status_set('maintenance',
                   "Installing {} from elastic.co apt repos".format(
                       ELASTIC_PKG.capitalize()))
        charms.apt.queue_install([ELASTIC_PKG])
    set_flag('elastic.pkg.available')


@when_any('deb.installed.{}'.format(ELASTIC_PKG),
          'apt.installed.{}'.format(ELASTIC_PKG))
@when_not('elastic.base.available')
def set_elastic_base_available():
    set_flag('elastic.base.available')
