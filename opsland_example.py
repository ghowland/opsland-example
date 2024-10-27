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

from logic import utility

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
  
  # If we got an input file, load it
  if config.input != None:
    input_path = config.input
    config.input = utility.LoadJson(config.input)
    if config.input == None:
      LOG.error(f'Failed to load JSON: {input_path}')
      sys.exit(1)
    else:
      LOG.debug(f'Loaded Input: {input_path}  Input: {config.input}')

  # Testing
  if config.command == 'go': ExecuteCommand(config, command_go.Go)
  elif config.command == 'deep': ExecuteCommand(config, command_go.Deep)
  elif config.command == '2x': ExecuteCommand(config, command_go.Transform2x)
  elif config.command == 'crud_user': ExecuteCommand(config, command_go.Crud_User)

  # Site Fundamentals
  elif config.command == 'site_login': ExecuteCommand(config, command_go.Site_Login)
  elif config.command == 'site_editor': ExecuteCommand(config, command_go.Site_Editor)

  else: print(f'''{{"_error": "Unknown command: {config.command}"}}''')


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    prog='OpsLand Example',
    description='A CLI client for OpsLand, which is a web and threaded job server based on CLI output',
    epilog='A brief example in CLI-JSON and other output.')

  parser.add_argument('-d', '--debug', default=False, action='store_true', help='Debug logging')
  parser.add_argument('-i', '--input', default=None, help='Input JSON path, if present')
  parser.add_argument('command', help='Command to execute')
  args = parser.parse_args()
  Main(args)

