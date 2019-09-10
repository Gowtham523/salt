# -*- coding: utf-8 -*-
'''
Support REDFISH API commands. This module uses DMTF redfish python library 


:depends: Python module redfish.
    You can install redfish using pip:

    .. code-block:: bash

        pip install redfish

:configuration: The following configuration defaults can be
    define (pillar or config files):

    .. code-block:: python

        ipmi.config:
            redfish_host: 127.0.0.1
            redfish_user: root
            redfish_password: apassword

    Usage can override the config defaults:

    .. code-block:: bash

            salt-call get.get_bootdev api_host=myipmienabled.system
                                    api_user=admin api_pass=pass
                                    uid=1
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt libs
from salt.ext import six

def __virtual__():

    IMPORT_ERR = None
    try:
        import requests
        import logging
        import json
        import os

    except Exception as ex:
        IMPORT_ERR = six.text_type(ex)
    return (IMPORT_ERR is None, IMPORT_ERR)



def PowerOn(name, **kwargs):
    '''
    Get current boot device override information.

    Provides the current requested boot device.  Be aware that not all IPMI
    devices support this.  Even in BMCs that claim to, occasionally the
    BIOS or UEFI fail to honor it. This is usually only applicable to the
    next reboot.

    :param kwargs:
        - redfish_host=127.0.0.1
        - redfish_user=root
        - redfish_pass=calvin

    CLI Example:

    .. code-block:: bash

        salt-call redfish.get_bootdev api_host=https://100.98.4.77 api_user=admin api_pass=pass
    '''
    ret = {'name': 'get_ResetTypes', 'result': False, 'comment': '', 'changes': {} }
    sysinfo = __salt__['redfish.get_SystemInfo'](**kwargs)
    if sysinfo["PowerState"] == "On":
        ret['result'] = True
        ret['comment'] = 'system already in PowerOn state'
        return ret
    elif sysinfo["PowerState"] == "Off":
        power_on = __salt__['redfish.system_reset'](reset_type="On",**kwargs)
        ret['result'] = True
        ret['comment'] = 'set to power on'
        ret['changes']["PowerState"] =  "On"
        return ret
    return ret
