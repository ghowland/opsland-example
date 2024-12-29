from logic.command_go import *


def Space_ProductStock(config):
  """Register ProductStocks"""
  # Start with the pass through and mutate
  all_product_stocks = config.input.get('existing', {})
  if not all_product_stocks: all_product_stocks = {}

  if '__time' in all_product_stocks: del all_product_stocks['__time']

  request = config.input.get('request', {})

  # If we have a new product_stock, and its non-empty and > 3 chars
  if '__add.new.product_stock_name' in request and len(request['__add.new.product_stock_name'].strip()) > 3:
    new_product_stock = request['__add.new.product_stock_name']

    found_uuid = GetProductStockByName(all_product_stocks, new_product_stock)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_product_stocks)
      new_data = CreateNewProductStock(new_uuid, new_product_stock)

      # Add the new product_stock
      all_product_stocks[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_product_stock.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_product_stocks:
        all_product_stocks[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_product_stock.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_product_stocks:
        del all_product_stocks[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_product_stock_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_product_stocks:
        if path in all_product_stocks[target_uuid]['details']:
          all_product_stocks[target_uuid]['details'].remove(path)
  
  # Update Edits
  UpdateEdits(all_product_stocks, request)

  return all_product_stocks


def CreateNewProductStock(new_uuid, product_stock_name):
  """"""
  data = {'uuid': new_uuid, 'name': product_stock_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetProductStockByName(all_product_stocks, product_stock_name):
  """"""
  for product_stock_uuid, product_stock_data in all_product_stocks.items():
    if product_stock_data['name'] == product_stock_name:
      return product_stock_uuid
  
  return None



def UpdateEdits(all_product_stocks, request):
  """Process the `__edit` stuff"""
  # Look for delete
  for item_key, item_data in request.items():
    if item_key.startswith('__edit.') and item_data.strip():
      target_uuid = item_key.split('.')[1]
      field = item_key.split('.')[2]

      if target_uuid in all_product_stocks:
        all_product_stocks[target_uuid][field] = item_data
