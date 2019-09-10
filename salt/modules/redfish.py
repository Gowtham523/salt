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


IMPORT_ERR = None
try:
    import redfish
#    from pyghmi.ipmi.private import session
except Exception as ex:
    IMPORT_ERR = six.text_type(ex)
import redfish
import logging
import requests
import json
import os
log = logging.getLogger(__name__)

__virtualname__ = 'redfish'


def __virtual__():
    return (IMPORT_ERR is None, IMPORT_ERR)


def _get_config(**kwargs):
    '''
    Return configuration
    '''
    config = {
        'redfish_host': 'https://100.98.4.77',
        'redfish_user': 'root',
        'redfish_password': 'calvin',
    }
    if '__salt__' in globals():
        config_key = '{0}.config'.format(__virtualname__)
        config.update(__salt__['config.get'](config_key, {}))
    for k in set(config) & set(kwargs):
        config[k] = kwargs[k]
    return config

class _RedfishSession(object):

    #def _onlogon(self, response):
    #    if 'error' in response:
    #        raise Exception(response['error'])

    def __init__(self, **kwargs):
        #self.connection = None
        config = _get_config(**kwargs)
        self.connection = redfish.redfish_client(base_url=config['redfish_host'], username=config['redfish_user'], \
                          password=config['redfish_password'], default_prefix='/redfish/v1')
        self.connection = self.connection.login(auth="session")

    #def __exit__(self, type, value, traceback):
    #    if self.connection:
    #        self.connection.logout()
    def _get(self,uri):
        response= requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']))
        return response['Boot']

def get_ResetTypes(**kwargs):
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
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    

    return {'ResetType': response['Actions']['#ComputerSystem.Reset']['ResetType@Redfish.AllowableValues']}

def get_BootSources(**kwargs):
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    return {'BootSources': response['Boot']['BootSourceOverrideTarget@Redfish.AllowableValues']}

def get_SystemInfo(**kwargs):
    sysinfo={}
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    sysinfo['AssetTag']=response['AssetTag']
    sysinfo['BiosVersion'] = response['BiosVersion']
    sysinfo['HostName'] = response['HostName']
    sysinfo['Manufacturer'] = response['Manufacturer']
    sysinfo['MemorySummary'] = response['MemorySummary']
    sysinfo['Model'] = response['Model']
    sysinfo['PartNumber'] = response['PartNumber']
    sysinfo['PowerState'] = response['PowerState']
    sysinfo['ProcessorSummary'] = response['ProcessorSummary']
    sysinfo['SKU'] = response['SKU']
    sysinfo['SerialNumber'] = response['SerialNumber']
    sysinfo['UUID'] = response['UUID']
    sysinfo['SystemType'] = response['SystemType']
    sysinfo['Status'] = response['Status']
    
    return sysinfo

def system_reset(reset_type, **kwargs):
    sysinfo={}
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    payload = {'ResetType': '%s'% reset_type }
    headers = {'content-type': 'application/json'}

    response = requests.post(config['redfish_host']+uri, data=json.dumps(payload), headers=headers, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    return { 'system_reset': response }
def set_OneTimeBoot(boot_source, boot_mode,  **kwargs):
    uri="/redfish/v1/Systems/System.Embedded.1"
    headers = {'content-type': 'application/json'} 
    config = _get_config(**kwargs)
    if boot_mode == 'Uefi':
        payload = {"Boot":{"BootSourceOverrideTarget": "UefiTarget","UefiTargetBootSourceOverride": "%s" % boot_source}}
    else:
        payload = {"Boot":{"BootSourceOverrideTarget": "%s" % boot_source}} 
    response = requests.patch(config['redfish_host']+uri, data=json.dumps(payload), headers=headers, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    return { 'OneTimeBoot': response }

def get_EthernetInterfaces(**kwargs):
    nics={}
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    for nic in response["Members"]:
        
        nic_response = requests.get(config['redfish_host']+nic["@odata.id"], auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
        nics[os.path.basename(nic["@odata.id"])]=nic_response

    return {'EthernetInterfaces': nics }

def get_system_CooledBy(**kwargs):
    cooling={}
    config = _get_config(**kwargs)
    uri="/redfish/v1/Systems/System.Embedded.1"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    for fan in response['Links']["CooledBy"]:
        cooling_response = requests.get(config['redfish_host']+fan["@odata.id"], auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
        cooling[os.path.basename(fan["@odata.id"])]=cooling_response
    return {'CooledBy': cooling }

def get_FirmwareInventory(**kwargs):
    firmwares={}
    config = _get_config(**kwargs)
    uri="/redfish/v1/UpdateService/FirmwareInventory/"
    response = requests.get(config['redfish_host']+uri, auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    for fw in response["Members"]:
        firmwares[os.path.basename(fw["@odata.id"])] = requests.get(config['redfish_host']+fw["@odata.id"], auth=(config['redfish_user'], config['redfish_password']),verify=False).json()
    return {"FirmwareInventory": firmwares }

    
    

        


        
    

