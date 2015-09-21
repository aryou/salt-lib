# -*- coding: utf-8 -*-
'''
AI Runner Functions
'''
from __future__ import absolute_import

# salt imports
import salt.config
import salt.loader
import salt.runner
import salt.client
import json
import pprint
import logging

__TOKEN__ = 'install_token'
__UUID__ = 'ose_uuid'

try:
    import pika
    HAS_PIKA = True
except ImportError:
    HAS_PIKA = False

log = logging.getLogger(__name__)

def __virtual__():
	return 'ai'

def add_ose(minion=None):
	'''
	Add New OSE to System MicroService
	'''
	if not minion:
		pprint.pprint("No Minion Specified\n")
		log.error('Missing minion arugment')
		return False

	log.info("Adding new minion '{0}' to System MicroService".format(minion))
	ret = _get_new_minion_data(minion)
	pprint.pprint(ret)
	return _send_rabbitmq(ret)

def _get_new_minion_data(minion=None):
	'''
	Get Initial Minion Data
	'''
	client = salt.client.LocalClient(__opts__['conf_file'])

	# first get token
	minion_token = client.cmd(minion, 'config.get', [__TOKEN__], timeout=1)
	token = minion_token.values()[0];

	# now get uuid
	minion_uuid = client.cmd(minion, 'config.get', [__UUID__], timeout=1)
	uuid = minion_uuid.values()[0];

	minions = client.cmd(minion, 'grains.items', timeout=1)
	ret = minions.values()[0];

	ret.update({'ose_uuid': uuid, 'install_token': token})
	return ret

def _send_rabbitmq(ret=None):
	'''
	Send RabbitMQ
	'''
	if not HAS_PIKA:
		pprint.pprint("Unable to Add OSE without PIKA module\n")
		log.error("Unable to create RabbitMQ Message: Pika not installed")
		return False

	master_opts = salt.config.client_config('/etc/salt/master')
	host = master_opts.get('runner.rabbitmq.host', None)
	vhost = master_opts.get('runner.rabbitmq.vhost', None)
	port = master_opts.get('runner.rabbitmq.port', None)
	user = master_opts.get('runner.rabbitmq.user', None)
	password = master_opts.get('runner.rabbitmq.password')
	exchange = master_opts.get('runner.rabbitmq.exchange', None)
	route_key = master_opts.get('runner.rabbitmq.route_key', None)
	
	if not all([host, vhost, port, user, password, exchange, route_key]):
		pprint.pprint("Missing Config Requirements\n")
		return False

	credentials = pika.PlainCredentials(user, password)
	params = pika.ConnectionParameters(host, port, vhost, credentials)
	conn = pika.BlockingConnection(params)
	channel = conn.channel()
	channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)

	message = json.dumps(ret)
	channel.basic_publish(exchange=exchange,
							routing_key=route_key,
	                      	body=message,
	                        properties=pika.BasicProperties(
                         		delivery_mode = 2,
                      		))
	conn.close()