from logic.command_go import *


def Space_User(config):
  """Register Products"""
  # Start with the pass through and mutate
  all_users = config.input.get('existing', {})
  if not all_users: all_users = {}

  if '__time' in all_users: del all_users['__time']

  request = config.input.get('request', {})

  # If we have a new user, and its non-empty and > 3 chars
  if '__add.new.user_name' in request and len(request['__add.new.user_name'].strip()) > 3:
    new_user = request['__add.new.user_name']

    found_uuid = GetUserByName(all_users, new_user)
    
    if found_uuid == None:
      new_uuid = utility.GetUUID(all_users)
      new_data = CreateNewUser(new_uuid, new_user)

      # Add the new user
      all_users[new_uuid] = new_data
  
  # Look for delete
  for item_key, item_data in request.items():
    # Add Page Path
    if item_key.startswith('__add_new_user.') and item_data.strip():
      target_uuid = item_key.split('.')[1]

      # Create the page_uri.  Always have the /, because otherwise the root is empty.  Can fix to mount as required later
      detail = item_data.strip()

      if target_uuid in all_users:
        all_users[target_uuid]['details'].append(detail)

    # Delete Domain
    elif item_key.startswith('__delete_user.'):
      target_uuid = item_key.split('.')[1]

      # If we have this, delete it
      if target_uuid in all_users:
        del all_users[target_uuid]    # Delete Domain

    # Delete Domain Path
    elif item_key.startswith('__delete_user_path.'):
      target_uuid = item_key.split('.')[1]
      path = item_key.split('.')[2]

      # If we have this, delete it
      if target_uuid in all_users:
        if path in all_users[target_uuid]['details']:
          all_users[target_uuid]['details'].remove(path)
  
  # Update Edits
  UpdateEdits(all_users, request)

  return all_users


def CreateNewUser(new_uuid, user_name):
  """"""
  #TODO: What if we used the parent_uuid for something interesting?  But can have a better name: referrer_user_uuid, ...
  data = {'uuid': new_uuid, 'name': user_name, 'theme': 'default', 'details': [], 'parent_uuid': None}

  return data


def GetUserByName(all_users, user_name):
  """"""
  for user_uuid, user_data in all_users.items():
    if user_data['name'] == user_name:
      return user_uuid
  
  return None



def UpdateEdits(all_users, request):
  """Process the `__edit` stuff"""
  # Look for delete
  for item_key, item_data in request.items():
    if item_key.startswith('__edit.') and item_data.strip():
      target_uuid = item_key.split('.')[1]
      field = item_key.split('.')[2]

      if target_uuid in all_users:
        all_users[target_uuid][field] = item_data
