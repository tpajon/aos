#!/usr/bin/python3
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):

  ansi_re = [
      # check ECMA-48 Section 5.4 (Control Sequences)
    re.compile(br'(\x1b\[\?1h\x1b=)'),
    re.compile(br'((?:\x9b|\x1b\x5b)[\x30-\x3f]*[\x20-\x2f]*[\x40-\x7e])'),
    re.compile(br'\x08.')
  ]

  terminal_stdout_re = [
    re.compile(br"[\r\n]?[\w]*\(.+\)\s*[\^\*]?(?:\[.+\])? ?#(?:\s*)$"),
    re.compile(br"[pP]assword:$"),
    re.compile(br"(?<=\s)[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\s*#\s*$"),
    re.compile(br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$"), # NOQA
    re.compile(br"[\r\n]?[\w]*(.+)?#(?:\s*)$")
  ]

  terminal_stderr_re = [
    re.compile(br"% ?Error"),
    re.compile(br"Error:", re.M),
    re.compile(br"^% \w+", re.M),
    re.compile(br"% ?Bad secret"),
    re.compile(br"invalid input", re.I),
    re.compile(br"(?:incomplete|ambiguous) command", re.I),
    re.compile(br"connection timed out", re.I),
    re.compile(br"[^\r\n]+ not found", re.I),
    re.compile(br"'[^']' +returned error code: ?\d+"),
  ]

  terminal_initial_prompt = b'Press any key to continue'

  terminal_initial_answer = b'\r'

  terminal_inital_prompt_newline = False

  def on_open_shell(self):
    try:
      self._exec_cli_command(b'no pag')
    except AnsibleConnectionFailure:
      self._connection.queue_message('warning', 'Unable '
                                      'to configure paging, command '
                                      'responses may be truncated')

  def on_become(self, passwd=None):
    '''
    Priveleged mode
    '''
    return

  def on_unbecome(self):
    '''
    Come out of priveleged mode
    '''
    return
