#!/usr/bin/env bash
# -*- coding: utf-8 -*-

tar zxf dependency/pexpect-4.6.tar.gz -C ./dependency/
tar zxf dependency/ptyprocess-0.6.0.tar.gz -C ./dependency/
ln -s ./dependency/pexpect-4.6/pexpect ./pexpect
ln -s ./dependency/ptyprocess-0.6.0/ptyprocess ./ptyprocess
