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

.. raw:: html
    <table border=0 cellpadding=0 class="documentation-table">
      <tr>
        <th colspan="2">Parameter</th>
        <th>Choices/<font color="blue">Defaults</font></th>
        <th width="100%">Comments</th>
      </tr>

      <tr>
        <td colspan="2">
          <div class="ansibleOptionAnchor" id="parameter-"></div>
          <b>commands</b>
          <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
          <div style="font-size: small">
            <span style="color: purple">list</span>
            / <span style="color: purple">elements=raw</span>
            / <span style="color: red">required</span>
          </div>
        </td>
        <td></td>
        <td>
          <div>List of commands to send to the remote aos device over the configured provider. The resulting output from the command is returned. If the <em>wait_for</em> argument is provided, the module is not returned until the condition is satisfied or the number of retries has expired. If a command sent to the device requires answering a prompt, it is possible to pass a dict containing <em>command</em>, <em>answer</em> and <em>prompt</em>. Common answers are &#x27;y&#x27; or &quot;\r&quot; (carriage return, must be double quotes). See examples.</div>
        </td>
      </tr>
      
      <tr>
         <td colspan="2">
            <div class="ansibleOptionAnchor" id="parameter-"></div>
            <b>interval</b>
            <a class="ansibleOptionLink" href="#parameter-" title="Permalink to this option"></a>
            <div style="font-size: small">
               <span style="color: purple">integer</span>
            </div>
         </td>
         <td>
            <b>Default:</b><br/><div style="color: blue">1</div>
         </td>
         <td>
            <div>Configures the interval in seconds to wait between retries of the command. If the command does not pass the specified conditions, the interval indicates how long to wait before trying the command again.</div>
         </td>
         </tr>
    </table>
    <br/>

Notes
-----

.. note::
  - This module works with connection ``network_cli``.
  - For more information on using Ansible to manage network devices see the :ref:`Ansible Network Guide <network_guide>`
