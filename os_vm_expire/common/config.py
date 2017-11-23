# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configuration setup for os-vm-expire.
"""

import logging
import os

from oslo_config import cfg
from oslo_log import log
from oslo_middleware import cors
from oslo_service import _options

from os_vm_expire import i18n as u
import os_vm_expire.version


MAX_VM_DURATION_DAYS=60
MAX_VM_EXTEND_DAYS=30

context_opts = [
    cfg.StrOpt('admin_role', default='admin',
               help=u._('Role used to identify an authenticated user as '
                        'administrator.')),
    cfg.BoolOpt('allow_anonymous_access', default=False,
                help=u._('Allow unauthenticated users to access the API with '
                         'read-only privileges. This only applies when using '
                         'ContextMiddleware.')),
]

common_opts = [
    cfg.IntOpt('max_vm_duration',
               default=MAX_VM_DURATION_DAYS,
               help=u._("Maximum life duration of VM in days")
    ),
    cfg.IntOpt('max_vm_extend',
               default=MAX_VM_EXTEND_DAYS,
               help=u._("Maximum life extend of VM in days")
    )
]

host_opts = [
    cfg.StrOpt('host_href', default='http://localhost:9311',
               help=u._("Host name, for use in HATEOAS-style references Note: "
                        "Typically this would be the load balanced endpoint "
                        "that clients would use to communicate back with this "
                        "service. If a deployment wants to derive host from "
                        "wsgi request instead then make this blank. Blank is "
                        "needed to override default config value which is "
                        "'http://localhost:9311'")),
]


db_opts = [
    cfg.StrOpt('sql_connection',
               default="sqlite:///osvmexpire.sqlite",
               secret=True,
               help=u._("SQLAlchemy connection string for the reference "
                        "implementation registry server. Any valid "
                        "SQLAlchemy connection string is fine. See: "
                        "http://www.sqlalchemy.org/docs/05/reference/"
                        "sqlalchemy/connections.html#sqlalchemy."
                        "create_engine. Note: For absolute addresses, use "
                        "'////' slashes after 'sqlite:'.")),
    cfg.IntOpt('sql_idle_timeout', default=3600,
               help=u._("Period in seconds after which SQLAlchemy should "
                        "reestablish its connection to the database. MySQL "
                        "uses a default `wait_timeout` of 8 hours, after "
                        "which it will drop idle connections. This can result "
                        "in 'MySQL Gone Away' exceptions. If you notice this, "
                        "you can lower this value to ensure that SQLAlchemy "
                        "reconnects before MySQL can drop the connection.")),
    cfg.IntOpt('sql_max_retries', default=60,
               help=u._("Maximum number of database connection retries "
                        "during startup. Set to -1 to specify an infinite "
                        "retry count.")),
    cfg.IntOpt('sql_retry_interval', default=1,
               help=u._("Interval between retries of opening a SQL "
                        "connection.")),
    cfg.BoolOpt('db_auto_create', default=True,
                help=u._("Create the osvmexpire database on service startup.")),
    cfg.IntOpt('max_limit_paging', default=100,
               help=u._("Maximum page size for the 'limit' paging URL "
                        "parameter.")),
    cfg.IntOpt('default_limit_paging', default=10,
               help=u._("Default page size for the 'limit' paging URL "
                        "parameter.")),
    cfg.StrOpt('sql_pool_class', default="QueuePool",
               help=u._("Accepts a class imported from the sqlalchemy.pool "
                        "module, and handles the details of building the "
                        "pool for you. If commented out, SQLAlchemy will "
                        "select based on the database dialect. Other options "
                        "are QueuePool (for SQLAlchemy-managed connections) "
                        "and NullPool (to disabled SQLAlchemy management of "
                        "connections). See http://docs.sqlalchemy.org/en/"
                        "latest/core/pooling.html for more details")),
    cfg.BoolOpt('sql_pool_logging', default=False,
                help=u._("Show SQLAlchemy pool-related debugging output in "
                         "logs (sets DEBUG log level output) if specified.")),
    cfg.IntOpt('sql_pool_size', default=5,
               help=u._("Size of pool used by SQLAlchemy. This is the largest "
                        "number of connections that will be kept persistently "
                        "in the pool. Can be set to 0 to indicate no size "
                        "limit. To disable pooling, use a NullPool with "
                        "sql_pool_class instead. Comment out to allow "
                        "SQLAlchemy to select the default.")),
    cfg.IntOpt('sql_pool_max_overflow', default=10,
               help=u._("# The maximum overflow size of the pool used by "
                        "SQLAlchemy. When the number of checked-out "
                        "connections reaches the size set in sql_pool_size, "
                        "additional connections will be returned up to this "
                        "limit. It follows then that the total number of "
                        "simultaneous connections the pool will allow is "
                        "sql_pool_size + sql_pool_max_overflow. Can be set "
                        "to -1 to indicate no overflow limit, so no limit "
                        "will be placed on the total number of concurrent "
                        "connections. Comment out to allow SQLAlchemy to "
                        "select the default.")),
]


def list_opts():
    yield None, context_opts
    yield None, common_opts
    yield None, host_opts
    yield None, db_opts
    yield None, _options.eventlet_backdoor_opts



# Flag to indicate  configuration is already parsed once or not
_CONFIG_PARSED_ONCE = False


def parse_args(conf, args=None, usage=None, default_config_files=None):
    global _CONFIG_PARSED_ONCE

    if default_config_files is None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists('/etc/os-vm-expire/osvmexpire.conf'):
            default_config_files = ['/etc/os-vm-expire/osvmexpire.conf']
        elif os.path.exists(os.path.join(dir_path, '../../etc/os-vm-expire/osvmexpire.conf')):
            default_config_files = [os.path.join(dir_path, '../../etc/os-vm-expire/osvmexpire.conf')]
        elif os.path.exists(os.path.join(dir_path, '../../osvmexpire.conf')):
            default_config_files = [os.path.join(dir_path, '../../osvmexpire.conf')]

    conf(args=args if args else [],
         project='os-vm-expire',
         prog='os-vm-expire',
         version=os_vm_expire.version.__version__,
         usage=usage,
         default_config_files=default_config_files)

    conf.pydev_debug_host = os.environ.get('PYDEV_DEBUG_HOST')
    conf.pydev_debug_port = os.environ.get('PYDEV_DEBUG_PORT')

    # Assign cfg.CONF handle to parsed configuration once at startup
    # only. No need to keep re-assigning it with separate plugin conf usage
    if not _CONFIG_PARSED_ONCE:
        cfg.CONF = conf
        _CONFIG_PARSED_ONCE = True


def new_config():
    conf = cfg.ConfigOpts()
    log.register_options(conf)
    conf.register_opts(context_opts)
    conf.register_opts(common_opts)
    conf.register_opts(host_opts)
    conf.register_opts(db_opts)
    conf.register_opts(_options.eventlet_backdoor_opts)
    conf.register_opts(_options.periodic_opts)

    conf.register_opts(_options.ssl_opts, "ssl")


    # Update default values from libraries that carry their own oslo.config
    # initialization and configuration.
    set_middleware_defaults()

    return conf


def setup_remote_pydev_debug():
    """Required setup for remote debugging."""

    if CONF.pydev_debug_host and CONF.pydev_debug_port:
        try:
            try:
                from pydev import pydevd
            except ImportError:
                import pydevd

            pydevd.settrace(CONF.pydev_debug_host,
                            port=int(CONF.pydev_debug_port),
                            stdoutToServer=True,
                            stderrToServer=True)
        except Exception:
            LOG.exception('Unable to join debugger, please '
                          'make sure that the debugger processes is '
                          'listening on debug-host \'%(debug-host)s\' '
                          'debug-port \'%(debug-port)s\'.',
                          {'debug-host': CONF.pydev_debug_host,
                           'debug-port': CONF.pydev_debug_port})
            raise


def set_middleware_defaults():
    """Update default configuration options for oslo.middleware."""
    cors.set_defaults(
        allow_headers=['X-Auth-Token',
                       'X-Openstack-Request-Id',
                       'X-Project-Id',
                       'X-Identity-Status',
                       'X-User-Id',
                       'X-Storage-Token',
                       'X-Domain-Id',
                       'X-User-Domain-Id',
                       'X-Project-Domain-Id',
                       'X-Roles'],
        expose_headers=['X-Auth-Token',
                        'X-Openstack-Request-Id',
                        'X-Project-Id',
                        'X-Identity-Status',
                        'X-User-Id',
                        'X-Storage-Token',
                        'X-Domain-Id',
                        'X-User-Domain-Id',
                        'X-Project-Domain-Id',
                        'X-Roles'],
        allow_methods=['GET',
                       'PUT',
                       'POST',
                       'DELETE',
                       'PATCH']
    )

CONF = new_config()
LOG = logging.getLogger(__name__)
parse_args(CONF)

# Adding global scope dict for all different configs created in various
# modules.
_CONFIGS = {}


def set_module_config(name, module_conf):
    """Each plugin can set its own conf instance with its group name."""
    _CONFIGS[name] = module_conf


def get_module_config(name):
    """Get handle to plugin specific config instance by its group name."""
    return _CONFIGS[name]
