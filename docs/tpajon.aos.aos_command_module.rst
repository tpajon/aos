.. _aos.aos_command_module:

**********************
tpajon.aos.aos_command
**********************

**Run commands on remote devices running Aruba OS**

Version added: 1.0.0

.. contents::
   :local:
   :depth: 1

Synopsis
--------
- Sends arbitrary commands to an aos node and returns the results read from the device. This module includes an argument that will cause the module to wait for a specific condition before returning or timing out if the condition is not met.

Parameters
----------

  +--------------+------------------+-----------------------------------------------------------------------------------------------+
  | Parameter    | Choices/Defaults | Comments                                                                                      |
  +==============+==================+===============================================================================================+
  | **commands** |                  | List of commands to send to the remote ios device over the configured provider. The resulting |
  |              |                  |                                                                                               |
  | list         |                  |                                                                                               |
  |              |                  |                                                                                               |
  | elements=raw |                  |                                                                                               |
  +--------------+------------------+-----------------------------------------------------------------------------------------------+

Notes
-----

.. note::
  - This module works with connection ``network_cli``.
  - For more information on using Ansible to manage network devices see the :ref:`Ansible Network Guide <network_guide>`
