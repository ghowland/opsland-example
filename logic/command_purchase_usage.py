from logic.command_go import *


def Space_Purchase_Usage(config):
  """Register PurchaseUsages"""
  # Start with the pass through and mutate
  all_purchase_usages = config.input.get('existing', {})
  if not all_purchase_usages: all_purchase_usages = {}

  if '__time' in all_purchase_usages: del all_purchase_usages['__time']

  request = config.input.get('request', {})

  # If we have a new purchase_usage, and its non-empty and > 3 chars
  if '__add.new.purchase_usage_name' in request and len(request['__add.new.purchase_usage_name'].strip()) > 3:
    new_purchase_usage = request['__add.new.purchase_usage_name']

    found_uuid = GetPurchaseUsageByName(all_purchase_usages, new_purchase_usage)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_purchase_usages)
      new_data = CreateNewPurchaseUsage(new_uuid, new_purchase_usage)

      # Add the new purchase_usage
      all_purchase_usages[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_purchase_usage.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_purchase_usages:
        all_purchase_usages[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_purchase_usage.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_purchase_usages:
        del all_purchase_usages[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_purchase_usage_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_purchase_usages:
        if path in all_purchase_usages[target_uuid]['details']:
          all_purchase_usages[target_uuid]['details'].remove(path)

  return all_purchase_usages


def CreateNewPurchaseUsage(new_uuid, purchase_usage_name):
  """"""
  data = {'uuid': new_uuid, 'name': purchase_usage_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetPurchaseUsageByName(all_purchase_usages, purchase_usage_name):
  """"""
  for purchase_usage_uuid, purchase_usage_data in all_purchase_usages.items():
    if purchase_usage_data['name'] == purchase_usage_name:
      return purchase_usage_uuid
  
  return None

