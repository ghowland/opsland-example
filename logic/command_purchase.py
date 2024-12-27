from logic.command_go import *


def Space_Purchase(config):
  """Register Purchases"""
  # Start with the pass through and mutate
  all_purchases = config.input.get('existing', {})
  if not all_purchases: all_purchases = {}

  if '__time' in all_purchases: del all_purchases['__time']

  request = config.input.get('request', {})

  # If we have a new purchase, and its non-empty and > 3 chars
  if '__add.new.purchase_name' in request and len(request['__add.new.purchase_name'].strip()) > 3:
    new_purchase = request['__add.new.purchase_name']

    found_uuid = GetPurchaseByName(all_purchases, new_purchase)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_purchases)
      new_data = CreateNewPurchase(new_uuid, new_purchase)

      # Add the new purchase
      all_purchases[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_purchase.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_purchases:
        all_purchases[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_purchase.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_purchases:
        del all_purchases[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_purchase_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_purchases:
        if path in all_purchases[target_uuid]['details']:
          all_purchases[target_uuid]['details'].remove(path)

  return all_purchases


def CreateNewPurchase(new_uuid, purchase_name):
  """"""
  data = {'uuid': new_uuid, 'name': purchase_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetPurchaseByName(all_purchases, purchase_name):
  """"""
  for purchase_uuid, purchase_data in all_purchases.items():
    if purchase_data['name'] == purchase_name:
      return purchase_uuid
  
  return None

