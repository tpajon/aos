#!/usr/bin/python
from __future__ import absolute_import, division, print_function
from unittest import result

__metaclass__ = type
DOCUMENTATION = '''
module: aos_command
author: Thomas PAJON (@tpajon)
short_description: Run commands on remote devices running Aruba OS
description:
- Sends arbitrary commands to an aos node and returns the results read from the device.
  This module includes an argument that will cause the module to wait for a specific
  condition before returning or timing out if the condition is not met.
version_added: 1.0.0
notes:
  - This module works with connection C(network_cli).
options:
  commands:
    description:
    - List of commands to send to the remote ios device over the configured provider.
      The resulting output from the command is returned. If the I(wait_for) argument
      is provided, the module is not returned until the condition is satisfied or
      the number of retries has expired. If a command sent to the device requires
      answering a prompt, it is possible to pass a dict containing I(command), I(answer)
      and I(prompt). Common answers are 'y' or "\\r" (carriage return, must be double
      quotes). See examples.
    required: true
    type: list
    elements: raw
  wait_for:
    description:
    - List of conditions to evaluate against the output of the command. The task will
      wait for each condition to be true before moving forward. If the conditional
      is not true within the configured number of retries, the task fails. See examples.
    aliases:
    - waitfor
    type: list
    elements: str
  match:
    description:
    - The I(match) argument is used in conjunction with the I(wait_for) argument to
      specify the match policy.  Valid values are C(all) or C(any).  If the value
      is set to C(all) then all conditionals in the wait_for must be satisfied.  If
      the value is set to C(any) then only one of the values must be satisfied.
    default: all
    type: str
    choices:
    - any
    - all
  retries:
    description:
    - Specifies the number of retries a command should by tried before it is considered
      failed. The command is run on the target device every retry and evaluated against
      the I(wait_for) conditions.
    default: 10
    type: int
  interval:
    description:
    - Configures the interval in seconds to wait between retries of the command. If
      the command does not pass the specified conditions, the interval indicates how
      long to wait before trying the command again.
    default: 1
    type: int
'''
EXAMPLES = '''
- name: run show version on remote devices
  tpajon.aos.aos_command:
    commands: show version

- name: run show version and check to see if output contains WC
  tpajon.aos.aos_command:
    commands: show version
    wait_for: result[0] contains WC

- name: run multiple commands on remote nodes
  tpajon.aos.aos_command:
    commands:
    - show version
    - show interfaces all

- name: run multiple commands and evaluate the output
  tpajon.aos.aos_command:
    commands:
    - show version
    - show interfaces all
    wait_for:
    - result[0] contains WC
    - result[1] contains "port 2"
'''
RETURN = '''
stdout:
  description: The set of responses from the commands
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: ['...', '...']
stdout_lines:
  description: The value of stdout split into a list
  returned: always apart from low level errors (such as action plugin)
  type: list
  sample: [['...', '...'], ['...'], ['...']]
failed_conditions:
  description: The list of conditionals that have failed
  returned: failed
  type: list
  sample: ['...', '...']
'''
import time
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.parsing import Conditional
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import transform_commands, to_lines
from ansible_collections.tpajon.aos.plugins.module_utils.network.aos.aos import aos_argument_spec, run_commands


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
