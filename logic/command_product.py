from logic.command_go import *


def Space_Product(config):
  """Register Products"""
  # Start with the pass through and mutate
  all_products = config.input.get('existing', {})
  if not all_products: all_products = {}

  if '__time' in all_products: del all_products['__time']

  request = config.input.get('request', {})

  # If we have a new product, and its non-empty and > 3 chars
  if '__add.new.product_name' in request and len(request['__add.new.product_name'].strip()) > 3:
    new_product = request['__add.new.product_name']

    found_uuid = GetProductByName(all_products, new_product)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_products)
      new_data = CreateNewProduct(new_uuid, new_product)

      # Add the new product
      all_products[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_product.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_products:
        all_products[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_product.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_products:
        del all_products[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_product_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_products:
        if path in all_products[target_uuid]['details']:
          all_products[target_uuid]['details'].remove(path)
  
  # Update Edits
  UpdateEdits(all_products, request)

  return all_products


def CreateNewProduct(new_uuid, product_name):
  """"""
  data = {'uuid': new_uuid, 'name': product_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetProductByName(all_products, product_name):
  """"""
  for product_uuid, product_data in all_products.items():
    if product_data['name'] == product_name:
      return product_uuid
  
  return None



def UpdateEdits(all_products, request):
  """Process the `__edit` stuff"""
  # Look for delete
  for item_key, item_data in request.items():
    if item_key.startswith('__edit.') and item_data.strip():
      target_uuid = item_key.split('.')[1]
      field = item_key.split('.')[2]

      if target_uuid in all_products:
        all_products[target_uuid][field] = item_data
