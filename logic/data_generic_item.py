from logic.command_go import *


def Generic_Item(config, add_item_key, delete_item_key):
  """Process items generically, we get their unique values as args"""
  # Start with the pass through and mutate
  all_vendors = config.input.get('existing', {})
  if not all_vendors: all_vendors = {}

  if '__time' in all_vendors: del all_vendors['__time']

  request = config.input.get('request', {})

  # If we have a new vendor, and its non-empty and > 3 chars
  if add_item_key in request and len(request[add_item_key].strip()) > 3:
    new_vendor = request[add_item_key]

    found_uuid = GetVendorByName(all_vendors, new_vendor)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_vendors)
      new_data = CreateNewVendor(new_uuid, new_vendor)

      # Add the new vendor
      all_vendors[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_vendor.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_vendors:
        all_vendors[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_vendor.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_vendors:
        del all_vendors[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith(delete_item_key):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_vendors:
        if path in all_vendors[target_uuid]['details']:
          all_vendors[target_uuid]['details'].remove(path)
  
  # Update Edits
  UpdateEdits(all_vendors, request)

  return all_vendors


def CreateNewVendor(new_uuid, vendor_name):
  """"""
  data = {'uuid': new_uuid, 'name': vendor_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetVendorByName(all_vendors, vendor_name):
  """"""
  for vendor_uuid, vendor_data in all_vendors.items():
    if vendor_data['name'] == vendor_name:
      return vendor_uuid
  
  return None


def UpdateEdits(all_vendors, request):
  """Process the `__edit` stuff"""
  # Look for delete
  for item_key, item_data in request.items():
    if item_key.startswith('__edit.') and item_data.strip():
      target_uuid = item_key.split('.')[1]
      field = item_key.split('.')[2]

      if target_uuid in all_vendors:
        all_vendors[target_uuid][field] = item_data

