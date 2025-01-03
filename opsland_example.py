#!/usr/bin/env python3.12

"""
OpsLand Example: A basic program that has different commands to output different JSON and other values to test a OpsLand bundle

Requirements:
  pip3.12 install -r requirements.txt
"""

import argparse
import sys
import json
import pprint

from logic import command_go
from logic import command_product
from logic import command_user
from logic import command_purchase
from logic import command_purchase_usage
from logic import command_account
from logic import command_product_stock
from logic import command_vendor

from logic import utility

from logic import log
from logic.log import LOG


def ProcessCommands(config):
  """Process the command.  Routing, basically."""
  # Testing
  if config.command == 'go': ExecuteCommand(config, command_go.Go)
  elif config.command == 'deep': ExecuteCommand(config, command_go.Deep)
  elif config.command == '2x': ExecuteCommand(config, command_go.Transform2x)
  elif config.command == 'crud_user': ExecuteCommand(config, command_go.Crud_User)

  # Site Fundamentals
  elif config.command == 'site_login': ExecuteCommand(config, command_go.Site_Login)
  elif config.command == 'site_editor': ExecuteCommand(config, command_go.Site_Editor)
  elif config.command == 'site_editor_dynamic': ExecuteCommand(config, command_go.Site_Editor_Dynamic)

  # Site Page
  elif config.command == 'site_page': ExecuteCommand(config, command_go.Site_Page)

  # Old New
  elif config.command == 'site_page_example_render': ExecuteCommand(config, command_go.Site_Page_Example_Render)


  # Space
  elif config.command == 'space_page_data': ExecuteCommand(config, command_go.Space_Page_Data)
  elif config.command == 'space_map_widget_html': ExecuteCommand(config, command_go.Space_Map_Widget_HTML)
  elif config.command == 'space_widget_tags': ExecuteCommand(config, command_go.Space_Widget_Tags)
  elif config.command == 'space_widget_spec': ExecuteCommand(config, command_go.Space_Widget_Spec)
  elif config.command == 'space_style': ExecuteCommand(config, command_go.Space_Style)
  elif config.command == 'space_style_select_data': ExecuteCommand(config, command_go.Space_Style_Select_Data)
  elif config.command == 'space_content_data': ExecuteCommand(config, command_go.Space_Content_Data)
  elif config.command == 'site_content_register': ExecuteCommand(config, command_go.Space_Content_Register)
  elif config.command == 'site_content_derived': ExecuteCommand(config, command_go.Space_Content_Derived)
  elif config.command == 'content_derived_refresh': ExecuteCommand(config, command_go.Space_Content_Derived_Refresh)
  

  # Site Domains and Pages
  elif config.command == 'site_domain': ExecuteCommand(config, command_go.Space_Site_Domain)


  # Product
  elif config.command == 'site_product': ExecuteCommand(config, command_product.Space_Product)

  # Product Stock
  elif config.command == 'space_product_stock': ExecuteCommand(config, command_product_stock.Space_ProductStock)

  # Vendor
  elif config.command == 'space_vendor': ExecuteCommand(config, command_vendor.Space_Vendor)

  # User
  elif config.command == 'space_user': ExecuteCommand(config, command_user.Space_User)

  # Purchase
  elif config.command == 'space_purchase': ExecuteCommand(config, command_purchase.Space_Purchase)

  # Purchase Usage
  elif config.command == 'space_purchase_usage': ExecuteCommand(config, command_purchase_usage.Space_Purchase_Usage)

  # Account
  elif config.command == 'space_account': ExecuteCommand(config, command_account.Space_Account)


  # Content
  elif config.command == 'upload_refresh': ExecuteCommand(config, command_go.Upload_Refresh)
  elif config.command == 'table_data_refresh': ExecuteCommand(config, command_go.Table_Data_Refresh)
  elif config.command == 'cache_icons': ExecuteCommand(config, command_go.Cache_Icons)


  else: print(f'''{{"_error": "Unknown command: {config.command}"}}''')


def ExecuteCommand(config, exec_func):
  """Execute the command and dump JSON"""
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
      LOG.debug(f'Loaded Input: {input_path}\nInput: {pprint.pformat(config.input)}')

  # Progress the commands
  ProcessCommands(config)


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

