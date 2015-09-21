# -*- coding: utf-8 -*-
'''
To enable this returner the minion will need the pika installed and
the following values configured in the minion or master config:

.. code-block:: yaml

    returner.rabbitmq.host: 'salt'
    returner.rabbitmq.port: 5672
    returner.rabbitmq.user: 'salt'
    returner.rabbitmq.password: 'salt'
    returner.rabbitmq.exchange: 'salt.exchange'
    returner.rabbitmq.return_key: 'saltreturn'
'''
from __future__ import absolute_import

# Import python libs
from contextlib import contextmanager
import sys
import json
import logging

# Import salt libs
import salt.returners
import salt.utils.jid
import salt.exceptions

try:
    import pika
    HAS_PIKA = True
except ImportError:
    HAS_PIKA = False

__virtualname__ = 'rabbitmq'

def __virtual__():
    if not HAS_PIKA:
        return False
    return __virtualname__

def _get_options(ret=None):
    '''
    Get the postgres options from salt.
    '''
    defaults = {'host': None,
    			'port': 5672,
                'user': 'guest',
                'password': 'guest',
                'exchange': None,
                'return_key': None,
                'event_key': None,
                'jid_key': None}

    attrs = {'host': 'host',
            'port': 'port',
    		'vhost': 'vhost',
            'user': 'user',
            'password': 'password',
            'exchange': 'exchange',
            'return_key': 'return_key',
            'event_key': 'event_key',
            'jid_key': 'jid_key'}

    _options = salt.returners.get_returner_options('returner.{0}'.format(__virtualname__),
                                                   ret,
                                                   attrs,
                                                   __salt__=__salt__,
                                                   __opts__=__opts__,
                                                   defaults=defaults)
    # get minion install configs
    _options['install_token'] = __salt__['config.option']('install_token')
    _options['ose_uuid'] = __salt__['config.option']('ose_uuid')

    return _options

def _get_conn(ret=None):
    _options = _get_options(ret)
    host = _options.get('host')
    vhost = _options.get('vhost')
    user = _options.get('user')
    password = _options.get('password')
    port = _options.get('port')

    credentials = pika.PlainCredentials(user, password)
    return pika.BlockingConnection(pika.ConnectionParameters(
               host,
               port,
               vhost,
               credentials
               ))

def _close_conn(conn):
    '''
    Close the rabbitmq connection
    '''
    conn.close()

def returner(ret):
    '''
    Return data to a rabbitmq broker
    '''
    # get configs
    _options = _get_options(ret)
    return_key = _options.get('return_key')
    exchange = _options.get('exchange')

    if not return_key:
        return False

    conn = _get_conn()
    channel = conn.channel()
    channel.exchange_declare(exchange=exchange, type='direct', durable=True)
    ret['install_token'] = _options.get('install_token')
    ret['ose_uuid'] = _options.get('ose_uuid')
    message = json.dumps(ret)
    channel.basic_publish(exchange=exchange,
							routing_key=return_key,
	                      	body=message,
	                        properties=pika.BasicProperties(
                         		delivery_mode = 2,
                      		))
    _close_conn(conn)


def event_return(events):
	# get configs
    _options = _get_options(ret=None)
    event_key = _options.get('event_key')
    exchange = _options.get('exchange')
    
    if not event_key:
    	return False

    conn = _get_conn(ret=None)
    channel = conn.channel()
    channel.exchange_declare(exchange=exchange, type='direct', durable=True)
    for event in events:
			message = {'tag': event.get('tag', ''),
						'data': event.get('data', ''),
						'master_id': __opts__['id']}
			channel.basic_publish(exchange=exchange,
						routing_key=event_key,
                      	body=json.dumps(message),
                        properties=pika.BasicProperties(
                     		delivery_mode = 2,
                  		))
    _close_conn(conn)


