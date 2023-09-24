#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import re
import os
import subprocess
import sys
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_dir, './paidaxin'))
    import paidaxin
except ImportError:
    paidaxin = None

if not paidaxin:
    print('Please install paidaxin first.')
    sys.exit(1)


def restore_shadow_password(shadow_password):
    shadow_pw = '**ShadowPassword**'
    if shadow_password != shadow_pw:
        return shadow_password
    try:
        fpath = os.path.expanduser('~/pw')
        with open(fpath, "r") as fp:
            clear_text_pw = fp.read()
        return clear_text_pw
    except:
        return shadow_password


def run_local_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
    return (result.returncode == 0, result.stdout)


def run_remote_command(remote_run_info):
    ping_cmd = 'ping -c 4 -i 0.2 -W 1 -q {}'.format(remote_run_info['hostip'])
    if remote_run_info.get('jumpbox_user', None) and remote_run_info.get('jumpbox_ip', None):
        ping_cmd = 'ssh -o StrictHostKeyChecking=no {}@{} "{}"'.format(remote_run_info['jumpbox_user'], remote_run_info['jumpbox_ip'], ping_cmd)
    ping_result = '\d+\s+packets\s+transmitted,\s+(\d+) received,\s+\d+%\spacket\s+loss'
    _, msg = run_local_command(ping_cmd)
    match = re.search(ping_result, msg)
    if match:
        received = match.group(1)
    else:
        received = '0'
    if int(received) == 0:
        print('{} is unreachable.'.format(remote_run_info['hostip']))
        return False

    password = restore_shadow_password(remote_run_info['password'])

    login_cmd = 'sshpass -p {} ssh -o StrictHostKeyChecking=no'.format(password)
    if remote_run_info.get('jumpbox_user', None) and remote_run_info.get('jumpbox_ip', None):
        login_cmd += ' -J {}@{}'.format(remote_run_info['jumpbox_user'], remote_run_info['jumpbox_ip'])
    login_cmd += ' {}@{}'.format(remote_run_info['user'], remote_run_info['hostip'])

    cli = paidaxin.PaiDaXin()

    run_local_command('ssh-keygen -R {}'.format(remote_run_info['hostip'])) # Remove the old ssh key
    session = None
    try:
        session, output = cli.sendline(session, login_cmd,
                                       [["{}@{}'s password: ".format(remote_run_info['user'], remote_run_info['hostip']), password, True],
                                        ['{}@{}:~$ '.format(remote_run_info['user'], remote_run_info['hostname']),        None,     None]],
                                        quiet=True)
    except Exception as e:
        print('Failed to login {}, because of {}'.format(remote_run_info['hostip'], e))
        return False

    for command in remote_run_info['commands']:
        try:
            session, output = cli.sendline(session, command,
                                           [['{}@{}:~$ '.format(remote_run_info['user'], remote_run_info['hostname']), None, None]],
                                           quiet=True)
            print(output)
        except Exception as e:
            print('Failed to run command {}, because of {}'.format(command, e))
            return False

    return True


def parse_remote_run(infos):
    '''
    csv format:
    hostname, user, hostip, password, jumpbox_user, jumpbox_ip, jumpbox_password, command1[, command2, ...]
    '''
    parsed_data = []
    with open(infos, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        header = next(csv_reader)
        command_start_index = header.index('command1')
        for row in csv_reader:
            if row and not row[0].strip().startswith("#"):
                cleaned_row = [cell.strip() for cell in row]
                hostname, user, hostip, password, jumpbox_user, jumpbox_ip, jumpbox_password = cleaned_row[:7]
                commands = cleaned_row[command_start_index:]
                parsed_row = {
                    'hostname': hostname,
                    'user': user,
                    'hostip': hostip,
                    'password': password,
                    'jumpbox_user': jumpbox_user,
                    'jumpbox_ip': jumpbox_ip,
                    'jumpbox_password': jumpbox_password,
                    'commands': commands
                }
                parsed_data.append(parsed_row)
    return parsed_data


def main():

    if len(sys.argv) != 2:
        print("Usage: remote-run path_of_remote_run_info.csv")
        return
    else:
        remote_run_csv = sys.argv[1]


    for remote_run in parse_remote_run(remote_run_csv):
        print('\n======== {} ========'.format(remote_run['hostname']))
        run_remote_command(remote_run)


if __name__ == "__main__":
    main()

