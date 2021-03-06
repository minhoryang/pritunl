from pritunl.constants import *
from pritunl.exceptions import *
from pritunl.descriptors import *
from pritunl import utils
from pritunl import settings
from pritunl import server
from pritunl import organization
from pritunl import app
from pritunl import auth
from pritunl import __version__

@app.app.route('/status', methods=['GET'])
@auth.session_auth
def status_get():
    orgs_count = 0
    servers_count = 0
    servers_online_count = 0
    clients_count = 0
    clients = set()

    for svr in server.iter_servers():
        servers_count += 1
        if svr.status:
            servers_online_count += 1
        # MongoDict doesnt support set(svr.clients)
        clients = clients | set(svr.clients.keys())
    clients_count = len(clients)

    user_count = organization.get_user_count_multi()
    local_networks = utils.get_local_networks()

    if settings.local.openssl_heartbleed:
        notification = 'You are running an outdated version of openssl ' + \
            'containting the heartbleed bug. This could allow an attacker ' + \
            'to compromise your server. Please upgrade your openssl ' + \
            'package and restart the pritunl service.'
    else:
        notification = settings.local.notification

    return utils.jsonify({
        'org_count': orgs_count,
        'users_online': clients_count,
        'user_count': user_count,
        'servers_online': servers_online_count,
        'server_count': servers_count,
        'server_version': __version__,
        'current_host': settings.local.host_id,
        'public_ip': settings.local.public_ip,
        'local_networks': local_networks,
        'notification': notification,
    })
