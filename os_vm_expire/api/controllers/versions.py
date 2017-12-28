#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import pecan
from six.moves.urllib import parse

from os_vm_expire.api import controllers
from os_vm_expire.api.controllers import vmexclude
from os_vm_expire.api.controllers import vmexpire
from os_vm_expire.common import utils
from os_vm_expire import i18n as u
from os_vm_expire import version

LOG = utils.getLogger(__name__)


MIME_TYPE_JSON = 'application/json'
MIME_TYPE_JSON_HOME = 'application/json-home'
MEDIA_TYPE_JSON = 'application/vnd.openstack.key-manager-%s+json'


def _version_not_found():
    """Throw exception indicating version not found."""
    pecan.abort(404, u._("The version you requested wasn't found"))


def _get_versioned_url(version):
    if version[-1] != '/':
        version += '/'
    # If host_href is not set in osvmexpire conf,
    # then derive it from request url
    host_part = utils.get_base_url_from_request()
    if host_part[-1] != '/':
        host_part += '/'
    return parse.urljoin(host_part, version)


class BaseVersionController(object):
    """Base class for the version-specific controllers"""

    @classmethod
    def get_version_info(cls, request):
        return {
            'id': cls.version_id,
            'status': 'stable',
            'updated': cls.last_updated,
            'links': [
                {
                    'rel': 'self',
                    'href': _get_versioned_url(cls.version_string),
                }, {
                    'rel': 'describedby',
                    'type': 'text/html',
                    'href': 'https://docs.openstack.org/'
                }
            ],
            'media-types': [
                {
                    'base': MIME_TYPE_JSON,
                    'type': MEDIA_TYPE_JSON % cls.version_string
                }
            ]
        }


class V1Controller(BaseVersionController):
    """Root controller for the v1 API"""

    version_string = 'v1'

    # NOTE(jaosorior): We might start using decimals in the future, meanwhile
    # this is the same as the version string.
    version_id = 'v1'

    last_updated = '2017-11-22T00:00:00Z'

    def __init__(self):
        LOG.debug('=== Creating V1Controller ===')

    @pecan.expose(generic=True)
    def index(self):
        pecan.abort(405)  # HTTP 405 Method Not Allowed as default

    @pecan.expose()
    def _lookup(self, project_id, *remainder):
        if not project_id:
            return self.on_get()
        if remainder and remainder[0] == 'vmexpires':
            return vmexpire.VmExpireController(project_id), remainder
        elif remainder and remainder[0] == 'vmexcludes':
            return vmexclude.VmExcludeController(project_id), remainder
        else:
            return self.on_get()

    @index.when(method='GET', template='json')
    @utils.allow_certain_content_types(MIME_TYPE_JSON, MIME_TYPE_JSON_HOME)
    @controllers.handle_exceptions(u._('Version retrieval'))
    def on_get(self):
        pecan.core.override_template('json')
        return {'version': self.get_version_info(pecan.request)}


AVAILABLE_VERSIONS = {
    V1Controller.version_string: V1Controller,
}

DEFAULT_VERSION = V1Controller.version_string


class VersionsController(object):

    def __init__(self):
        LOG.debug('=== Creating VersionsController ===')

    @pecan.expose(generic=True)
    def index(self, **kwargs):
        pecan.abort(405)  # HTTP 405 Method Not Allowed as default

    @index.when(method='GET', template='json')
    @utils.allow_certain_content_types(MIME_TYPE_JSON, MIME_TYPE_JSON_HOME)
    def on_get(self, **kwargs):
        """The list of versions is dependent on the context."""
        self._redirect_to_default_json_home_if_needed(pecan.request)

        if 'build' in kwargs:
            return {'build': version.__version__}

        versions_info = [version_class.get_version_info(pecan.request) for
                         version_class in AVAILABLE_VERSIONS.values()]

        version_output = {
            'versions': {
                'values': versions_info
            }
        }

        # Since we are returning all the versions available, the proper status
        # code is Multiple Choices (300)
        pecan.response.status = 300
        return version_output

    def _redirect_to_default_json_home_if_needed(self, request):
        if self._mime_best_match(request.accept) == MIME_TYPE_JSON_HOME:
            url = _get_versioned_url(DEFAULT_VERSION)
            LOG.debug("Redirecting Request to " + url)
            # NOTE(jaosorior): This issues an "external" redirect because of
            # two reasons:
            # * This module doesn't require authorization, and accessing
            #   specific version info needs that.
            # * The resource is a separate app_factory and won't be found
            #   internally
            pecan.redirect(url, request=request)

    def _mime_best_match(self, accept):
        if not accept:
            return MIME_TYPE_JSON

        SUPPORTED_TYPES = [MIME_TYPE_JSON, MIME_TYPE_JSON_HOME]
        return accept.best_match(SUPPORTED_TYPES)
