#!/usr/bin/env python3

"""
OpsLand Example: A basic program that has different commands to output different JSON and other values to test a OpsLand bundle

Requirements:
  pip3.12 install -r requirements.txt
"""


import argparse
import sys
import json

from logic import command_go

from logic import log
from logic.log import LOG


def ExecuteCommand(config, exec_func):
  """"""
  result = exec_func(config)

  print(json.dumps(result))


def Main(config):
  if config.debug:
    log.SetLogLevel(log.logging.DEBUG)
    LOG.debug('Log level: Debug')

  if config.command == 'go': ExecuteCommand(config, command_go.Go)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    prog='OpsLand Example',
    description='A CLI client for OpsLand, which is a web and threaded job server based on CLI output',
    epilog='A brief example in CLI-JSON and other output.')

  parser.add_argument('-d', '--debug', default=False, action='store_true', help='Debug logging')
  parser.add_argument('command', help='Command to execute')
  args = parser.parse_args()
  Main(args)

