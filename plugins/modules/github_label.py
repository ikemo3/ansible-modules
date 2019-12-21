#!/usr/bin/env python3

# Copyright: (c) 2019, Hideki Ikemoto <ikemo333@gmail.com>
#
#  GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
module: github_label
short_description: View GitHub labels.
description:
    - View GitHub labels for a given repository and organization.
version_added: "2.10"
options:
  repo:
    description:
      - Name of repository from which labels needs to be retrieved.
    required: true
  organization:
    description:
      - Name of the GitHub organization in which the repository is hosted.
    required: true
  action:
    description:
        - Get various details about labels depending upon action specified.
    default: 'get_status'
    choices:
        - 'get_status'
author:
    - Hideki Ikemoto
'''

RETURN = '''
get_status:
    description: State of the GitHub labels
    type: str
    returned: success
    sample: open, closed
'''

EXAMPLES = '''
- name: Check if GitHub labels is closed or not
  github_label:
    organization: ansible
    repo: ansible
    action: get_status
  register: r
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization=dict(required=True),
            repo=dict(required=True),
            action=dict(choices=['get_status'], default='get_status'),
        ),
        supports_check_mode=True,
    )

    organization = module.params['organization']
    repo = module.params['repo']
    action = module.params['action']

    result = dict()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
    }

    url = "https://api.github.com/repos/%s/%s/labels" % (organization, repo)

    response, info = fetch_url(module, url, headers=headers)
    if not (200 <= info['status'] < 400):
        if info['status'] == 404:
            module.fail_json(msg="Failed to find labels")
        module.fail_json(msg="Failed to send request to %s: %s" % (url, info['msg']))

    gh_obj = json.loads(response.read())

    if action == 'get_status' or action is None:
        if module.check_mode:
            result.update(changed=True)
        else:
            labels = {}
            for gh_label in gh_obj:
                name = gh_label['name']
                description = gh_label['description']
                color = gh_label['color']
                default = gh_label['default']
                labels[name] = dict(description=description, color=color, default=default)
            result.update(changed=True, labels=labels)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
