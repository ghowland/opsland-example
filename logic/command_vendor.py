from logic.command_go import *

import logic.data_generic_item as data_generic_item

# Unique Data Keys for this data type, so they can be handled generically
ADD_ITEM_KEY = '__add.new.vendor_name'
DELETE_ITEM_KEY = '__delete_vendor_path.'


def Space_Vendor(config):
  """Register Vendors"""
  return data_generic_item.Generic_Item(config, ADD_ITEM_KEY, DELETE_ITEM_KEY)


