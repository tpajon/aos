#!/usr/bin/python3
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
author: tpajon
cliconf: aos
short_description: Use aos cliconf to run command on Aruba OS platform
description:
- This aos plugin provides low level abstraction apis for sending and receiving CLI
  commands from Aruba OS network devices.
options:
  config_commands:
    description:
    - Specifies a list of commands that can make configuration changes
      to the target device.
    - When `ansible_network_single_user_mode` is enabled, if a command sent
      to the device is present in this list, the existing cache is invalidated.
    version_added: 2.0.0
    type: list
    default: []
    vars:
    - name: ansible_aos_config_commands
'''

import re
import time
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.module_utils.common._collections_compat import Mapping
from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.config import NetworkConfig, dumps
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list
from ansible.plugins.cliconf import CliconfBase, enable_mode

class Cliconf(CliconfBase):
  def __init__(self, *args, **kwargs):
    self._device_info = {}
    super(Cliconf, self).__init__(*args, **kwargs)
  
  @enable_mode
  def get_config(self, source='running', flags=None, format=None):
    if source not in ('running', 'startup'):
      raise ValueError('fetching configuration from %s is not supported' % source)
    
    if format:
      raise ValueError('\'format\' value %s is not supported for get_config' % format)
    
    if not flags:
      flags = []
    if source == 'running':
      cmd = 'show running-config '
    else:
      cmd = 'show startup-config '
    
    cmd += ' '.join(to_list(flags))
    cmd = cmd.strip()

    return self.send_command(cmd)

  def get(
    self,
    command=None,
    prompt=None,
    answer=None,
    sendonly=False,
    output=None,
    newline=True,
    check_all=False
  ):
    if not command:
      raise ValueError('must provide value of command to execute')
    if output:
      raise ValueError('\'output\' value %s is not supported for get' % output)
    
    return self.send_command(
      command=command,
      prompt=prompt,
      answer=answer,
      sendonly=sendonly,
      newline=newline,
      check_all=check_all,
    )
  
  def get_device_info(self):
    if not self._device_info:
      device_info = {}

      device_info['network_os'] = 'aos'
      reply = self.get(command='show version')
      data = to_text(reply, errors='surrogate_or_strict').strip()
      match = re.search(r'[Nn]ame\s+: (\S+)', data)
      if match:
        device_info['network_os_hostname'] = match.group(1)
      
      match = re.search(r'[Ss]oftware revision\s+: (\S+)', data)
      if match:
        device_info['network_os_revision'] = match.group(1)
      
      match = re.search(r'ROM Version\s+: (\S+)', data, re.M)
      if match:
        device_info['network_os_version'] = match.group(1)
      
      self._device_info = device_info
    
    return self._device_info
  
  def get_device_operations(self):
    return {
      'supports_diff_replace': True,
      'supports_commit': False,
      'supports_rollback': False,
      'supports_defaults': True,
      'supports_onbox_diff': False,
      'supports_commit_comment': False,
      'supports_multiline_delimiter': True,
      'supports_diff_match': True,
      'supports_diff_ignore_lines': True,
      'supports_generate_diff': True,
      'supports_replace': False,
    }

  def get_option_values(self):
    return {
      'format': ['text'],
      'diff_match': ['line', 'strict', 'exact', 'none'],
      'diff_replace': ['line', 'block'],
      'output': [],
    }

  def get_capabilities(self):
    result = super(Cliconf, self).get_capabilities()
    result['rpc'] += [
      'edit_banner',
      'get_diff',
      'run_commands',
      'get_defaults_flag',
    ]
    result['device_operations'] = self.get_device_operations()
    result.update(self.get_option_values())
    return json.dumps(result)
  
  def run_commands(self, commands=None, check_rc=True):
    if commands is None:
      raise ValueError('\'commands\' value is required')
    
    responses = list()
    for cmd in to_list(commands):
      if not isinstance(cmd, Mapping):
        cmd = {'command': cmd}
      
      output = cmd.pop('output', None)
      if output:
        raise ValueError('\'output\' value %s is not supported for run_commands' % output)
    
      try:
        out = self.send_command(**cmd)
      except AnsibleConnectionFailure as e:
        if check_rc:
          raise
        out = getattr(e, 'err', to_text(e))
      
      responses.append(out)

    return responses
