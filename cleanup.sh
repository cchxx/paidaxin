#!/usr/bin/env bash
# -*- coding: utf-8 -*-

rm -fr pexpect
rm -fr ptyprocess
rm -fr ./dependency/pexpect-4.6
rm -fr ./dependency/ptyprocess-0.6.0
find . -iname "*.pyc" | xargs rm -fr
find . -iname "*.log" | xargs rm -fr
