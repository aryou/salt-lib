# -*- coding: utf-8 -*-
'''
MyRunner
'''
from __future__ import absolute_import

# Import salt modules
import salt.client

if __name__ == "__main__":
	print "WTF"

def __virtual__():
	return 'myrunner'

def up():
    '''
    Print a list of all of the minions that are up
    '''
    client = salt.client.LocalClient(__opts__['conf_file'])
    minions = client.cmd('*', 'test.ping', timeout=1)
    for minion in sorted(minions):
        print minion

def test():
	print "Hello World!"