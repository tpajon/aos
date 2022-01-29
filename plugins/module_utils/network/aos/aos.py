
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.connection import Connection, ConnectionError


aos_provider_spec = {
  'host': dict(),
  'port': dict(type='int'),
  'username': dict(fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
  'password': dict(fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True),
  'ssh_keyfile': dict(fallback=(env_fallback, ['ANSIBLE_NET_SSH_KEYFILE']), type='path'),
  'authorize': dict(default=False, fallback=(env_fallback, ['ANSIBLE_NET_AUTHORIZE']), type='bool'),
  'auth_pass': dict(fallback=(env_fallback, ['ANSIBLE_NET_AUTH_PASS']), no_log=True),
  'timeout': dict(type='int'),
}

aos_argument_spec = {
  'provider': dict(
    type='dict',
    options=aos_provider_spec,
    removed_at_date='2022-06-01',
    removed_from_collection='tpajon.aos'
  )
}

def get_connection(module):
  if hasattr(module, '_aos_connection'):
    return module._aos_connection
  
  capabilities = get_capabilities(module)
  network_api = capabilities.get('network_api')

  if network_api == 'cliconf':
    module._aos_connection = Connection(module._socket_path)
  else:
    module.fail_json(msg='Invalid connection type %s' % network_api)
  
  return module._aos_connection

def get_capabilities(module):
  if hasattr(module, '_aos_capabilities'):
    return module._aos_capabilities
  
  try:
    capabilities = Connection(module._socket_path).get_capabilities()
  except ConnectionError as exc:
    module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
  
  module._aos_capabilities = json.loads(capabilities)
  
  return module._aos_capabilities

def run_commands(module, commands, check_rc=True):
  connection = get_connection(module)

  try:
    connection.run_commands(commands=commands, check_rc=check_rc)
  except ConnectionError as exc:
    module.fail_json(msg=to_text(exc))