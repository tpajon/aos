#!/usr/bin/python
from __future__ import absolute_import, division, print_function
from unittest import result

__metaclass__ = type
DOCUMENTATION = ''''''
EXAMPLES = ''''''
RETURN = ''''''
import time
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import Conditional
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import transform_commands, to_lines
from tpajon.aos.plugins.module_utils.network.aos.aos import aos_argument_spec, run_commands


def parse_command(module: AnsibleModule, warnings: list):
  commands = transform_commands(module)

  if module.check_mode:
    for item in list(commands):
      if not item['command'].startswith('show'):
        warnings.append(
          'Only show commands are supported when using check mode, not executing %s'
          % item['command']
        )
        commands.remove(item)
  
  return commands

def main():
  ''' Main entrypoint for module execution
  '''
  argument_spec = dict(
    commands=dict(type='list', elements='raw', required=True),
    wait_for=dict(type='list', elements='str', aliaises=['waitfor']),
    match=dict(default='all', choices=['all', 'any']),
    retries=dict(default=10, type='int'),
    interval=dict(default=1, type='int'),
  )

  argument_spec.update(aos_argument_spec)
  
  module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
  warnings = list()
  result = { 'changed': False, 'warnings': warnings }
  commands = parse_command(module, warnings)
  wait_for = module.params['wait_for'] or list()

  try:
    conditionals = [ Conditional(c) for c in wait_for ]
  except AttributeError as exc:
    module.fail_json(msg=to_text(exc))
  
  retries = module.params['retries']
  interval = module.params['interval']
  match = module.params['match']

  while retries > 0:
    responses = run_commands(module, commands)

    for item in list(conditionals):
      if item(responses):
        if match == 'any':
          conditionals = list()
          break
        conditionals.remove(item)
    
    if not conditionals:
      break

    time.sleep(interval)
    retries -= 1
  
  if conditionals:
    failed_connections = [ item.raw for item in conditionals ]
    msg = 'One or more conditional statements have not been satisfied'

    module.fail_json(msg=msg, failed_connections=failed_connections)
  
  result.update(
    { 'stdout': responses, 'stdout_lines': list(to_lines(responses)) }
  )

  module.exit_json(**result)

if __name__ == '__main__':
  main()
