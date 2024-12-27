from logic.command_go import *


def Space_Account(config):
  """Register Accounts"""
  # Start with the pass through and mutate
  all_accounts = config.input.get('existing', {})
  if not all_accounts: all_accounts = {}

  if '__time' in all_accounts: del all_accounts['__time']

  request = config.input.get('request', {})

  # If we have a new account, and its non-empty and > 3 chars
  if '__add.new.account_name' in request and len(request['__add.new.account_name'].strip()) > 3:
    new_account = request['__add.new.account_name']

    found_uuid = GetAccountByName(all_accounts, new_account)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_accounts)
      new_data = CreateNewAccount(new_uuid, new_account)

      # Add the new account
      all_accounts[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_account.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_accounts:
        all_accounts[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_account.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_accounts:
        del all_accounts[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_account_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_accounts:
        if path in all_accounts[target_uuid]['details']:
          all_accounts[target_uuid]['details'].remove(path)

  return all_accounts


def CreateNewAccount(new_uuid, account_name):
  """"""
  data = {'uuid': new_uuid, 'name': account_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetAccountByName(all_accounts, account_name):
  """"""
  for account_uuid, account_data in all_accounts.items():
    if account_data['name'] == account_name:
      return account_uuid
  
  return None

