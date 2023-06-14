#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import pexpect
import re
import logging


PY3 = sys.version_info[0] >= 3

if PY3:
    string_types = str
else:
    string_types = basestring


class PaiDaXin ():

    def __init__(self, logger=None, unicode=True):
        self.unicode = unicode
        self.logger = None


    def _utf8(self, contents):
        if not self.unicode:
            return contents
        if isinstance(contents, string_types):
            return unicode(contents, 'utf-8')
        elif isinstance(contents, list):
            return [unicode(item, 'utf-8') for item in contents]
        else:
            return None


    def _spawn(self, command):
        if not self.unicode:
            return pexpect.spawn(command)
        else:
            return pexpect.spawnu(command)


    def clear(self, session):
        if session:
            session.expect(self._utf8('.*'))


    def wait(self, session, expectation, timeout=None):
        if session:
            exp = self._utf8(expectation)
            if timeout != None:
                session.expect(exp, timeout)
            else:
                session.expect(exp)

    def sendline(self, session, command, responses, timeout=-1):
        """
        examples of responses:
            [["Escape character is '^]'.", "",   True ],
             ["#",                         None, None ],
             ["[yes/no]:",                 "y",  False]]
        """
        reply_idx = 0
        subcmd_idx = 1
        wait_idx = 2
        sess = None
        if session:
            sess = session
            sess.expect(self._utf8('.*'))
            sess.sendline(command)
        else:
            sess = self._spawn(command)
            sess.logfile = sys.stdout

        waiting = []
        for response in responses:
            waiting.append(response[reply_idx])
        output = ''

        while True:
            index = sess.expect_exact(self._utf8(waiting), timeout=timeout)
            output += sess.before

            timeout = -1
            response = responses[index]
            if response[subcmd_idx]:
                time.sleep(1)
                sess.expect(self._utf8('.*'))
                sess.sendline(response[subcmd_idx])
                if response[wait_idx] == None or response[wait_idx] == False:
                    break
            else:
                break

        return (sess, output)

    def send(self, session, command, cr=False, lf=True):
        if session == None:
            return
        for c in command:
            session.send(c)
        if cr:
            session.send('\r')
        if lf:
            session.send('\n')


if __name__ == '__main__':
    print('TODO : main() of PaiDaXin')
