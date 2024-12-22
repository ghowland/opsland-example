"""
Commands: Go
"""


import pprint
import time
import os
import glob
import mistune
from mistune import HTMLRenderer

from PIL import Image

from logic import utility

from logic.log import LOG


#NOTE: On MacOS do these instructions for 0.95 or latest brew version: https://blog.dave-bell.co.uk/2020/01/06/using-mtr-on-os-x-without-sudo/
MTR_PATH = '/usr/local/bin/mtr'

WIDGET_WIDTH_OPTIONS = ['w-min', 'w-24', 'w-32', 'w-40', 'w-48', 'w-64', 'w-72', 'w-90', 'w-96', 'w-full']

WIDGET_HEIGHT_OPTIONS = ['h-min', 'h-24', 'h-32', 'h-40', 'h-48', 'h-64', 'h-72', 'h-90', 'h-96', 'h-full']

COLOR_VALUE_OPTIONS = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']

ROUNDED_OPTIONS = ['rounded-none', 'rounded-sm', 'rounded', 'rounded-md', 'rounded-lg', 'rounded-xl', 'rounded-2xl', 'rounded-full']

WIDGET_MARGIN_OPTIONS = ['m-0', 'm-2', 'm-4', 'm-6', 'm-8', 'm-12', 'm-16', 'm-24', 'm-32']

WIDGET_PADDING_OPTIONS = ['p-0', 'p-2', 'p-4', 'p-6', 'p-8', 'p-12', 'p-16', 'p-24', 'p-32']

BOLD_OPTIONS = ['', 'font-thin', 'font-normal', 'font-medium', 'font-semibold', 'font-bold', 'font-extrabold', 'font-black']

TEXT_ALIGNMENT_OPTIONS = ['text-left', 'text-left', 'text-center', 'text-justify', 'text-right']

TEXT_SIZE_OPTIONS = ['text-xs', 'text-sm', 'text-base', 'text-lg', 'text-xl', 'text-2xl', 'text-3xl', 'text-4xl', 'text-5xl', 'text-6xl', 'text-7xl', 'text-8xl', 'text-9xl']

# Default value for missing color_value
DEFAULT_COLOR_VALUE = 50

# Path to load different widget data type
PATH_WIDGET_DATA_FORMAT = 'data/widget_data/{name}.yaml'

# Default new widget
DEFAULT_NEW_WIDGET = 'card0'

# A list of all the page content data
PATH_WIDGET_SPECS = 'data/widget_specs.yaml'

# Page Content
PATH_MAP_WIDGET_HTML = 'data/map_widget_html.yaml'

# Content Data Type
PATH_CONTENT_DATA = 'data/content_data.yaml'

# Tags
PATH_TAGS = 'data/tags.yaml'

# Example render data
PATH_EXAMPLE_RENDER = 'data/example_page_render.yaml'

# How we get default values for any type of data.  Simple lookup table per type
PATH_DATA_VAR_DEFAULTS = 'data/data_var_defaults.yaml'
DATA_VAR_DEFAULTS = utility.LoadYaml(PATH_DATA_VAR_DEFAULTS)

# Styles
STYLES = ['default', 'alternate', 'headline', 'section_head', 'title', 'big', 'small', 'extra_small', 'highlight', 'disabled', 'warning', 'attract', 'hero', 'promotion', 'premium', 
          'boost', 'spotlight', 'callout', 'exclusive', 'engage', 'iconic', 'launch', 'vivid', 'vip', 'curated', 'impact', 'limited', 'conversion', 'security', 'problem', 'error', 
          'critical_failure', 'verification_required', 'access_denied', 'data_breach_alert', 'blocked', 'update_required', 'maintenance_mode', 'recover_account', 
          'custom_00', 'custom_01', 'custom_02']

# Upload Path
UPLOAD_PATH = '/mnt/d/_OpsLand/uploads/'
UPLOAD_THUMBNAIL_PATH = '/mnt/d/_OpsLand/uploads/thumbnail/'
# Content path for files, after we move them
CONTENT_PATH = '/mnt/d/_OpsLand/content/'
CONTENT_DERIVED_PATH = '/mnt/d/_OpsLand/derived/'

# Upload Thumbnail size
DEFAULT_THUMB_SIZE = [320, 240]

# Style Select Data 
PATH_STYLE_SELECT_DATA = 'data/select_data.yaml'

# Glob for Table Data to load
GLOB_TABLE_DATA = 'data/table_data/*.yaml'

# Glob for all the icons
GLOB_ICONS = 'data/icons/*/*/*.svg'


def Space_Content_Derived_Refresh(config):
  """Refresh derived"""
  # Ensure we have a dictionary to start with
  # result = config.input.get('existing', [])
  # if not result: result = []

  result = []

  paths = os.listdir(CONTENT_DERIVED_PATH)
  for path in paths:
    full_path = CONTENT_DERIVED_PATH + path

    # Skip directories or anything not a file
    if not os.path.isfile(full_path): continue

    stat_data = os.stat(full_path)
    # LOG.info(f'Stat: {stat_data}')

    path_data = {'path': path, 'size': stat_data.st_size, 'created': stat_data.st_ctime}

    # # Create thumbnail
    # thumb_path = UPLOAD_THUMBNAIL_PATH+path
    # CreateThumbnail(full_path, thumb_path)

    result.append(path_data)

  return result


def Space_Content_Derived(config):
  """Register content"""
  request_input = utility.LoadJsonFromString(config.input['request']['request_input'])

  LOG.info(f'Input request: {pprint.pformat(request_input)}')

  # Start with the pass through and mutate
  result = config.input.get('existing', {})
  if not result: result = {}

  # Pass this through
  result['request_input'] = request_input

  return result


def Space_Content_Register(config):
  """Register content"""
  # Start with the pass through and mutate
  result = config.input.get('existing', {})
  if not result: result = {}

  # Content upload just happened
  request = config.input['request']
  if 'type' in request and 'filename' in request:
    LOG.info(f'''Type: {request['type']}  File: {request['filename']}''')

    # Ensure a new unique UUID
    uuid = None
    while uuid == None or uuid in result:
      uuid = utility.GetUUID()

    # Check if this file already exists?  No, it's a new upload, who cares?
    pass

    # Create the content
    content = CreateContentObject(uuid, request['type'], request['filename'])
    if content:
      # Add the content item
      result[uuid] = content
  
  # Update Values
  UpdateValues(result, request)

  # Update Derived
  UpdateDerived(result, config.input['derived'])

  return result


def UpdateDerived(all_content, derived):
  """Add derived"""
  LOG.info(f'Derived: {derived}')

  for item_uuid, item_data in all_content.items():
    if item_uuid.startswith('_'): continue

    # Ensure we have a derived list
    if 'derived' not in item_data: item_data['derived'] = []
    if 'parent_uuid' not in item_data: item_data['parent_uuid'] = None

    # Look for any derived items
    for derived_item in derived:
      parts = derived_item['path'].split('__')
      parent_uuid = parts[0]
      derived_uuid = parts[1].split('.')[0]

      # If this is the parent of this item, add it
      if parent_uuid == item_uuid and derived_uuid not in item_data['derived']:
        item_data['derived'].append(derived_uuid)

  # Add derived content
  for derived_item in derived:
    # Get our parent and derived
    parts = derived_item['path'].split('__')
    parent_uuid = parts[0]
    derived_uuid = parts[1].split('.')[0]

    # Add this missing derived content
    if derived_uuid not in all_content:
      # Create the content
      content = CreateContentObject(derived_uuid, 'derived_image', derived_item['path'], parent_uuid)
      if content:
        # Add the content item
        all_content[derived_uuid] = content


def UpdateValues(all_content, request):
  """Update content from our request"""
  for key, value in request.items():
    # Skip empty updates
    #TODO: This isnt going to work in all our cases.  Need a null instead...
    if value == '' or '.' not in key: continue

    parts = key.split('.')

    # Skip if this is not a `__command.UUID.field` format

    uuid = parts[1]

    # We dont always have a field
    if len(parts) >= 3:
      field = parts[2]
    else:
      field = None

    # Fix the fieldname if we have collisions
    prefix = ''
    if field == 'label_site':
      field = 'labels'
      prefix = 'site:'
    elif field == 'label_custom':
      field = 'labels'
      prefix = 'custom:'

    # Set a value
    if key.startswith('__set.') and request['__command'] == 'set':
      if uuid in all_content:
        all_content[uuid][field] = value
      else:
        LOG.error(f'Missing content UUID, cant update: {uuid}   Request: {key} == {value}')

    # Add a value to a list
    elif key.startswith('__add.') and request['__command'] == 'set':
      if uuid in all_content:
        # Ensure we have a list to our our value
        if field not in all_content[uuid]:
          all_content[uuid][field] = []

        # If we dont already have it, then add it
        if f'{prefix}{value}' not in all_content[uuid][field]:
          all_content[uuid][field].append(f'{prefix}{value}')
      else:
        LOG.error(f'Missing content UUID, cant update: {uuid}   Request: {key} == {value}')
    
    # Add or update a custom tag
    elif key.startswith('__custom_tag.') and request['__command'] == 'set':
      try:
        index = int(field)
        # If this is a new item, append it
        if index == -1:
          all_content[uuid]['tags'].append(value)
        
        # Else, update the value
        elif index < len(all_content[uuid]['tags']):
          all_content[uuid]['tags'][index] = value
        
        # Else, failed
        else:
          LOG.error(f'''Index is outside the list length, cant set __custom_tag: {field}  Index: {index}  Len: {len(all_content[uuid]['tags'])}  Error: {e}''')

      except Exception as e:
        LOG.error(f'Index is not integer, cant set __custom_tag: {field}  Error: {e}')

    # Delete Tag
    elif key.startswith('__delete_tag.') and request['__command'] == 'delete':
      all_content[uuid]['tags'].remove(value)

    # Delete Label
    elif key.startswith('__delete_label.') and request['__command'] == 'delete':
      all_content[uuid]['labels'].remove(value)

    # Delete Content
    elif key.startswith('__delete_content.') and request['__command'] == 'delete':
      # Delete the primary path
      DeleteContentDataAndFiles(all_content, uuid)


def DeleteContentDataAndFiles(all_content, uuid):
  """Delete..."""
  content = all_content.get(uuid, None)
  if content is None: return

  if content['parent_uuid'] is None:
    full_path = f'''{CONTENT_PATH}/{content['path']}'''
  else:
    full_path = f'''{CONTENT_DERIVED_PATH}/{content['path']}'''

  # Find any derived content from this one
  for test_uuid, test_content in list(all_content.items()):
    if not test_uuid.startswith('_') and test_content['parent_uuid'] == uuid:
      DeleteContentDataAndFiles(all_content, test_uuid)

  # If we have the file, remove it
  if os.path.exists(full_path):
    # Remove the file
    os.remove(full_path)

    # Delete the content from our records
    del all_content[uuid]


def CreateContentObject(uuid, file_type, file_name, parent_uuid=None):
  """Create the content object from the request"""
  # Content
  content = {'uuid': uuid,
             'labels': [], 'tags': [],
             'priority': 0, 'cost': 0, 'cost_type': 'usd', 
             'duration': None, 'size': 0, 'size_type': 'none', 'rating': 0, 'rating_count': 0,
             # If this is data, then we reference if through the cache
             'cache_key': None, 'cache_unique_key': None, 'cache_unique_key_index': None,
             # `path` is where the file content is, and `filename` is the original name
             'path': None, 'filename': None,
             # If this has derived content, of this is derived content `parent_uuid`
             'derived': [], 'parent_uuid': parent_uuid,
            }

  # Save the filename, if we had one.  Should normally be the case, always?
  content['filename'] = file_name

  # Image
  if file_type == 'image':
    # Set the generated label for Image
    content['labels'].append('gen:image')

    # Image/PNG
    if file_name.lower().endswith('.png'):
      content['labels'].append('gen:image/png')
      content['path'] = f'{uuid}.png'

    # Image/JPG
    elif file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
      content['labels'].append('gen:image/jpg')
      content['path'] = f'{uuid}.jpg'

    # Image/GIF
    elif file_name.lower().endswith('.gif'):
      content['labels'].append('gen:image/gif')
      content['path'] = f'{uuid}.gif'

    # Image/BMP
    elif file_name.lower().endswith('.bmp'):
      content['labels'].append('gen:image/bmp')
      content['path'] = f'{uuid}.bmp'
  
  # Derived Image (Cropped)
  elif file_type == 'derived_image':
    # Set the generated label for Image
    content['labels'].append('gen:image')
    content['labels'].append('gen:image/png')
    content['labels'].append('gen:derived')
    content['path'] = file_name

  
  # Move the file into its content location and UUID name
  if parent_uuid == None:
    up_path = UPLOAD_PATH + file_name
    content_path = CONTENT_PATH + content['path']

    # Make sure we have the source path, then move it
    if os.path.exists(up_path):
      LOG.info(f'Upload: {up_path}  Content: {content_path}')
      os.rename(up_path, content_path)

      return content

    # Else, failed, dont try to do anything
    else:
      LOG.error(f'Failed to find upload file, shouldnt happen: {up_path}')
      return None
  
  # Else, this is derived content, and doesnt need to be moved.  Always return it
  else:
    return content


def Site_Content_Admin(config):
  """This is the data for ALL the content, and it edits data fields, or adds/removes, whatever.  Label management as well, since `limit` must be upheld

  `limit` and `limit_queue`, where we insert new elements into the front of the queue, so it bumps the old.  `limit` causes additions to fail until 1 is removed.  Make that easy, viewer-select

  """
  # Start with the pass through and mutate
  result = config.input['existing']
  
  return result


def Space_Content_Data(config):
  """Data schema for our core records, that other sources can map their data to, or edit in our system."""
  result = utility.LoadYaml(PATH_CONTENT_DATA)
  
  return result


def Cache_Icons(config):
  """"""
  data = {}

  paths = glob.glob(GLOB_ICONS)

  for path in paths:
    parts = path.replace('.svg', '').split('/')
    LOG.info(f'Parts: {parts}')

    with open(path) as stream:
      content = stream.read()

      item = {'html': content, 'style': parts[2], 'group': parts[3], 'name': parts[4].lower()}
      data[item['name']] = item

  return data


def Table_Data_Refresh(config):
  """"""
  data = {}

  paths = glob.glob(GLOB_TABLE_DATA)
  for path in paths:
    path_data = utility.LoadYaml(path)

    data[path_data['name']] = path_data

  return data


def Space_Style_Select_Data(config):
  """Styling options for Select HTML widgets"""
  result = {}

  result = utility.LoadYaml(PATH_STYLE_SELECT_DATA)

  return result


def Upload_Refresh(config):
  """Refresh files and thumbnails after an upload"""
  # Ensure we have a dictionary to start with
  # result = config.input.get('existing', [])
  # if not result: result = []

  result = []

  paths = os.listdir(UPLOAD_PATH)
  for path in paths:
    full_path = UPLOAD_PATH + path

    # Skip directories or anything not a file
    if not os.path.isfile(full_path): continue

    stat_data = os.stat(full_path)
    # LOG.info(f'Stat: {stat_data}')

    path_data = {'path': path, 'size': stat_data.st_size, 'created': stat_data.st_ctime}

    # Create thumbnail
    thumb_path = UPLOAD_THUMBNAIL_PATH+path
    CreateThumbnail(full_path, thumb_path)


    result.append(path_data)

  return result


def CreateThumbnail(full_path, thumb_path):
  """Create a thumbnail for an image, to a path"""
  # If the thumb already exists, return
  if os.path.exists(thumb_path): return

  img = Image.open(full_path)

  # Ensure correct orientation for camera photos EXIF data
  if img._getexif():
    if img._getexif().get(274) == 3:
        img = img.rotate(180, expand=True)
    elif img._getexif().get(274) == 6:
        img = img.rotate(270, expand=True)
    elif img._getexif().get(274) == 8:
        img = img.rotate(90, expand=True)

  # LOG.info(f'Looking for: {thumb_path}  Making from: {full_path}')
  max_size = list(DEFAULT_THUMB_SIZE)

  (width, height) = img.size

  # Landscape crop
  if width > height:
    # crop_y = height * size_ratio
    size_ratio = height / width
    max_size[1] = int(max_size[1] * size_ratio)
    
  # Portrait crop (or square)
  else:
    # crop_x = width / size_ratio
    size_ratio = width / height
    max_size[0] = int(max_size[0] * size_ratio)

  img_resize = img.resize(max_size)

  LOG.info(f'Size: [{width}, {height}]  Max Size: {max_size}  Ratio: {size_ratio}  Final Size: {img_resize.size}')

  img_resize.save(thumb_path)


def Space_Style(config):
  """Save our styling data"""
  # LOG.info(f'Input: {config.input}')

  # Pass through to start
  styles = dict(config.input.get('style_data', {}).get('actual', {}))
  control = dict(config.input.get('style_data', {}).get('merged', {}))

  # We assume we to update our data this time
  do_update_data = True

  # If we are changing styles, then dont update any data now
  if '__control.style' in config.input['request'] and config.input['request']['__control.style'] != config.input['request']['__control.current_style']:
    LOG.info(f'''Changing styles: From: {config.input['request']['__control.current_style']}  To: {config.input['request']['__control.style']}''')
    do_update_data = False

  # Set the styles
  style = config.input['request']['__control.style']

  LOG.info(f'Current Style: {style}')

  # If this is the first time we've set this style, create the dict
  if style not in styles:
    styles[style] = {}
  
  # Assign our current style for update
  cur_style = styles[style]

  # If we want to update the data, do it.  If we just changed keys, we want the page to load fresh data and submit again, so we dont do anything now
  if do_update_data:
    for key, value in config.input['request'].items():
      if key.startswith('__style.'):
        cur_style[key] = value

  # Take the actual and create a merged section, so this isnt tricky in Jinja
  (merged, merged_info) = MergeStylesWithParentData(styles)

  result = {'actual': styles, 'merged': merged, 'merged_info': merged_info}

  # Save the current style, so it passes through to the web page, to come back here again
  result['__control.style'] = config.input['request']['__control.style']
  result['__current'] = style
  result['__control.current_style'] = style

  return result


def MergeStylesWithParentData(styles):
  """Merge all the stylse """
  merged = {}
  info = ''

  styles_wait_parent_list = []
  styles_processed = []

  # Walk the list first, and find any that havent had their parents processed yet we put them into `styles_wait_parent_list` and process them later
  for style in STYLES:
    # Get the style data, or empty dict
    style_data = styles.get(style, {})

    # If this is default, accept as-is.  It must be complete as it's the basis for everything else
    if style == 'default':
      merged['default'] = style_data
      styles_processed.append(style)

    # Else, If it's parent was already processed
    elif style_data.get('__style.style.parent', 'default') in styles_processed:
      # Merge Parent to Child, and mark processed for others to use as parent
      merged[style] = MergeStyleParentToChild(styles, style_data.get('__style.style.parent', 'default'), style)
      styles_processed.append(style)

    # Else, defer this style until later
    else:
      styles_wait_parent_list.append(style)

  # Process any of the wait list styles, we keep processing this until we get them all, or just default the rest to `default` because there is a loop
  while styles_wait_parent_list:
    found_one = False

    for style in styles_wait_parent_list:
      style_data = styles.get(style, {})
      if style_data.get('__style.style.parent', 'default') in styles_processed:
        # Merge Parent to Child, and mark processed for others to use as parent
        merged[style] = MergeStyleParentToChild(styles, style_data.get('__style.style.parent', 'default'), style)
        styles_processed.append(style)
        found_one = True

    # We didnt find any, so take the first one in the list, and flip it to default and continue, until we process them all
    if not found_one:
      # Set the first item in the list to be parented, to default.  This is sure to complete, and then maybe others will, or the same will happen.  No problem
      styles_wait_parent_list[0]['__style.style.parent'] = 'default'
      
      # Feedback for the user to see we changed data
      info += f'Style parent set to default: `{style}`.  '

  return (merged, info)


def MergeStyleParentToChild(styles, parent_style, child_style):
  """"""
  merged = {}

  style_parent = styles.get(parent_style, {})
  style_child = styles.get(child_style, {})

  # Use the `default` entry keys for the master list of keys
  style_keys = style_parent.keys()

  # Loop over our master list of keys, so it's easy
  for style_key in style_keys:
    # Try to get from the child data
    merged[style_key] = style_child.get(style_key, 'parent')

    # If we want parent data, get from the parent
    if merged[style_key] in ('parent', ''):
      merged[style_key] = style_parent.get(style_key, 'parent')

  return merged


def Space_Page_Data(config):
  """This will be the new way to handle all page data.  Not the spec for widgets, but the data for this specific page"""
  # LOG.info(f'Input: {config.input}')

  # result = utility.LoadYaml(PATH_EXAMPLE_RENDER)
  result = config.input['site_page']
  result['map_widget_html'] = config.input['map_widget_html']
  result['widget_specs'] = config.input['widget_specs']
  
  # Update with the 'parents'
  UpdateWidgetsWithParents(result)

  result['uri'] = config.input['request']['site_page_uri']

  # Update over our original values
  update_data = UpdateWithEdits(config.input['request'], result['widgets'], result['map_widget_html'], result['widget_specs'])
  result.update(update_data)

  # Add widgets
  UpdateWithAddableWidgets(result)

  # Update with any special values (ex: markdown)
  UpdateWithSpecialValues(result)

  # Find all the referenced widgets, preparing to purge
  referenced_widgets = []
  FindReferencedWidgets(result, result['render'], referenced_widgets)

  # LOG.info(f'Found widgets referenced: {referenced_widgets}')

  # Purge unreferenced widgets
  PurgeUnreferencedWidgets(result, referenced_widgets)

  return result


def FindReferencedWidgets(data, widget_list, referenced_widgets):
  """Find all the referenced to widgets from our render list to the includes below"""
  for widget_id in widget_list:
    referenced_widgets.append(widget_id)

    # Loop over all the include dict-lists and find those too
    for include_key, include_widget_id_list in data['widgets'][widget_id]['include'].items():
      FindReferencedWidgets(data, include_widget_id_list, referenced_widgets)


def PurgeUnreferencedWidgets(data, referenced_widgets):
  """Remove all the widgets not in the referenced_widgets list"""
  purge_list = []

  for widget_id in data['widgets']:
    if widget_id not in referenced_widgets and widget_id not in purge_list:
      purge_list.append(widget_id)

  LOG.info(f'Purge Widget List: {purge_list}')

  # Delete unreferenced `widgets`
  for widget_id in list(data['widgets'].keys()):
    if widget_id not in referenced_widgets:
      LOG.info(f'Delete: widgets: {widget_id}')
      del data['widgets'][widget_id]

  # Delete unreferenced `parents`
  for widget_id in list(data['parents'].keys()):
    if widget_id not in referenced_widgets:
      LOG.info(f'Delete: parents: {widget_id}')
      del data['parents'][widget_id]

  # Delete unreferenced `include_widget_specs`
  for channel in list(data['include_widget_specs'].keys()):
    for widget_id in list(data['include_widget_specs'][channel].keys()):
      if widget_id not in referenced_widgets:
        LOG.info(f'Delete: include_widget_specs: {widget_id}')
        del data['include_widget_specs'][widget_id]

  # Delete unreferenced `include_options`
  for channel in list(data['include_options'].keys()):
    for widget_id in list(data['include_options'][channel].keys()):
      if widget_id not in referenced_widgets:
        LOG.info(f'Delete: include_options: {widget_id}')
        del data['include_options'][widget_id]


def UpdateWithAddableWidgets(data):
  """The purpose of this to to find all the widgets we could add, and then make a list to make it really easy to see what widgets could go where."""
  data['include_options'] = {}
  data['include_widget_specs'] = {}

  # LOG.info(f'Data: {pprint.pformat(data)}')

  # For every widget we have
  for (widget_id, widget_data) in data['widgets'].items():
    # Get their data
    widget_spec_instance = widget_data['widget']

    widget_html_mapping = data['map_widget_html'][widget_spec_instance]
    widget_spec = widget_html_mapping['spec']

    widget_spec_data = data['widget_specs'][widget_spec]

    # For each item they include
    for (include_target, include_data) in widget_spec_data['include'].items():
      # Test for tags
      if include_target not in data['include_options']:
        data['include_options'][include_target] = {}
      
      if include_target not in data['include_widget_specs']:
        data['include_widget_specs'][include_target] = {}
      
      # Save the list of tags
      include_widget_specs = GetWidgetSpecsByTagList(data['widget_specs'], include_data['tags'])
      data['include_widget_specs'][include_target][widget_id] = include_widget_specs

      # Add matching widget_html maps, by name, so we can reference them easily
      matched_maps = []
      # Starting with all the specs we allow...
      for include_widget_spec in include_widget_specs:
        # Check all the Widget HTML Maps, which are where the `spec` is defined, mapping an HTML file and a name, to a spec
        for (map_name, map_data) in data['map_widget_html'].items():
          if map_name.startswith('__'): continue

          # If this is spec matches are spec, we add it, if it isnt already there
          if map_data['spec'] == include_widget_spec and map_name not in matched_maps:
            matched_maps.append(map_name)
            # break

          #TODO:REMOVE: After above code is working, or this is forgotten, just delete.  It was from previous attempt          
          # LOG.info(f'Include Widget Spec: {include_widget_spec}')
          # LOG.info(f'Map Name: {map_name}   Map Data: {map_data}')
          # LOG.info(f'Widget Spec Data: {widget_spec_data}')

          # # If this is spec is in our tags, and it isnt a special var
          # if include_widget_spec in widget_spec_data['tags'] and not map_name.startswith('__'):
          #   matched_maps.append(map_name)

      # Add the maps we mathched above
      data['include_options'][include_target][widget_id] = matched_maps

      # Test for min

      # Test for max


def GetWidgetSpecsByTagList(widget_specs, tag_list):
  """"""
  final_specs = []

  for tag in tag_list:
    specs = GetWidgetSpecsByTag(widget_specs, tag)
    for spec in specs:
      if spec not in final_specs:
        final_specs.append(spec)

  return final_specs


def GetWidgetSpecsByTag(widget_specs, tag):
  """From a dictionary of `widget_specs` we look for a string `tag` in `widget_specs.tags`, and return the list that match."""
  specs = []

  LOG.debug(f'Widget Specs: {widget_specs}   Search: {tag}')

  for (spec_key, spec_data) in widget_specs.items():
    # Skip special data
    if spec_key.startswith('__'): continue

    LOG.debug(f'''Spec key: {spec_key}  Spec Data: {spec_data}''')
    LOG.debug(f'''Get Widget Spec by Tag: {tag}  In: {spec_data['tags']}''')

    if tag in spec_data['tags']:
      specs.append(spec_key)

  return specs


def UpdateWidgetsWithParents(data):
  """Add parents to the widgets"""
  data['parents'] = {}
  for widget_key, widget_data in data['widgets'].items():
    for include_key, include_widget_ids in widget_data['include'].items():
      for include_widget_id in include_widget_ids:
        data['parents'][include_widget_id] = widget_key

  return data



class MistuneMarkdownRenderer(HTMLRenderer):
  def codespan(self, text):
    if text.startswith('$') and text.endswith('$'):
      return f'''<span class="math">{ EscapeHTML(text) }</span>'''
    
    return '''<code>'''+ EscapeHTML(text) +'''</code>'''

  def paragraph(self, text):
    # Add line breaks
    text = text.replace('\n', '<br>')

    return '''<p class="
                        {% if cur_data.color and cur_data.color != 'parent' %} text-{{cur_data.color}}
                        {% else %}                                             text-{{cur_style['__style.text.color']}}   {% endif %}

                        {% if cur_style['__style.text.override_hover_color'] == 'true' %}hover:text-{{cur_style['__style.text.hover_color']}}{%endif%}
                        {% if cur_style['__style.text.override_focus_color'] == 'true' %}focus:text-{{cur_style['__style.text.focus_color']}}{%endif%}

                        {% if cur_data.margin and cur_data.margin != 'parent' %} {{cur_data.margin}}
                        {% else %}                                               {{cur_style['__style.text.margin']}}   {% endif %}

                        {% if cur_data.alignment and cur_data.alignment != 'parent' %} {{cur_data.alignment}}
                        {% else %}                                                     {{cur_style['__style.text.alignment']}}   {% endif %}

                        {% if cur_data.size and cur_data.size != 'parent' %} {{cur_data.size}}
                        {% else %}                                           {{cur_style['__style.text.size']}}   {% endif %}

                        {% if cur_data.bold and cur_data.bold != 'parent' %} {{cur_data.bold}}
                        {% else %}                                           {{cur_style['__style.text.bold']}}   {% endif %}

                        
                        {% if cur_data.transform and cur_data.transform != 'parent' %} {{cur_data.transform}}
                        {% else %}                                                     {{cur_style['__style.text.transform']}}   {% endif %}

                        {% if cur_data.decoration and cur_data.decoration != 'parent' %} {{cur_data.decoration}}
                        {% else %}                                                       {{cur_style['__style.text.decoration']}}   {% endif %}

                        {% if cur_data.font_style and cur_data.font_style != 'parent' %} {{cur_data.font_style}}
                        {% else %}                                                       {{cur_style['__style.text.font_style']}}   {% endif %}
              ">'''+ EscapeHTML(text) +'''</p>'''

  def text(self, text):
    return text

  def link(self, text, url, title=None):
    return f'''<a href="{url}" title="{title}" class="''' + '''
                        underline
                                                {% if cur_data.color and cur_data.color != 'parent' %} text-{{cur_data.color}}
                        {% else %}                                             text-{{cur_style['__style.text.color']}}   {% endif %}

                        {% if cur_style['__style.text.override_hover_color'] == 'true' %}hover:text-{{cur_style['__style.text.hover_color']}}{%endif%}
                        {% if cur_style['__style.text.override_focus_color'] == 'true' %}focus:text-{{cur_style['__style.text.focus_color']}}{%endif%}

                        {% if cur_data.margin and cur_data.margin != 'parent' %} {{cur_data.margin}}
                        {% else %}                                               {{cur_style['__style.text.margin']}}   {% endif %}

                        {% if cur_data.alignment and cur_data.alignment != 'parent' %} {{cur_data.alignment}}
                        {% else %}                                                     {{cur_style['__style.text.alignment']}}   {% endif %}

                        {% if cur_data.size and cur_data.size != 'parent' %} {{cur_data.size}}
                        {% else %}                                           {{cur_style['__style.text.size']}}   {% endif %}

                        {% if cur_data.bold and cur_data.bold != 'parent' %} {{cur_data.bold}}
                        {% else %}                                           {{cur_style['__style.text.bold']}}   {% endif %}

                        
                        {% if cur_data.transform and cur_data.transform != 'parent' %} {{cur_data.transform}}
                        {% else %}                                                     {{cur_style['__style.text.transform']}}   {% endif %}

                        {% if cur_data.font_style and cur_data.font_style != 'parent' %} {{cur_data.font_style}}
                        {% else %}                                                       {{cur_style['__style.text.font_style']}}   {% endif %}
              ">'''+ EscapeHTML(text) +'''</a>'''

  def linebreak(self):
    return f'''<br>'''

  def strong(self, text):
    return '''<strong class="
                        {% if cur_data.color and cur_data.color != 'parent' %} text-{{cur_data.color}}
                        {% else %}                                             text-{{cur_style['__style.text.color']}}   {% endif %}

                        {% if cur_style['__style.text.override_hover_color'] == 'true' %}hover:text-{{cur_style['__style.text.hover_color']}}{%endif%}
                        {% if cur_style['__style.text.override_focus_color'] == 'true' %}focus:text-{{cur_style['__style.text.focus_color']}}{%endif%}

                        {% if cur_data.alignment and cur_data.alignment != 'parent' %} {{cur_data.alignment}}
                        {% else %}                                                     {{cur_style['__style.text.alignment']}}   {% endif %}

                        {% if cur_data.size and cur_data.size != 'parent' %} {{cur_data.size}}
                        {% else %}                                           {{cur_style['__style.text.size']}}   {% endif %}

                        {% if cur_data.bold and cur_data.bold != 'parent' %} {{cur_data.bold}}
                        {% else %}                                           {{cur_style['__style.text.bold_strong']}}   {% endif %}

                        
                        {% if cur_data.transform and cur_data.transform != 'parent' %} {{cur_data.transform}}
                        {% else %}                                                     {{cur_style['__style.text.transform']}}   {% endif %}

                        {% if cur_data.decoration and cur_data.decoration != 'parent' %} {{cur_data.decoration}}
                        {% else %}                                                       {{cur_style['__style.text.decoration']}}   {% endif %}

                        {% if cur_data.font_style and cur_data.font_style != 'parent' %} {{cur_data.font_style}}
                        {% else %}                                                       {{cur_style['__style.text.font_style']}}   {% endif %}
              ">'''+ EscapeHTML(text) +'''</strong>'''
  
  def emphasis(self, text):
    return f'''<em class="text-blue-400">{ EscapeHTML(text) }</em>'''

  def image(self, alt, url, title=None):
    return f'<image class="text-blue-400" src="{url}" alt="{alt}" title="{title}">'''

  def heading(self, text, level, **attrs):
    return f'''<h class="text-blue-400">{ EscapeHTML(text) }</h>'''

  def block_quote(self, text):
    return f'''<quote class="text-blue-400">{ EscapeHTML(text) }</quote>'''

  def block_code(self, text):
    return f'''<code class="text-blue-400">{ EscapeHTML(text) }</code>'''

  def block_error(self, text):
    return f'''<error class="text-blue-400">{ EscapeHTML(text) }</error>'''


def EscapeHTML(text):
  """TODO: Write something useful here"""
  # Escape brackets
  return text


def UpdateWithSpecialValues(data):
  """"""
  map_widget_html = Space_Map_Widget_HTML(None)
  widget_specs = Space_Widget_Spec(None)

  markdown = mistune.create_markdown(renderer=MistuneMarkdownRenderer())

  # For all the widgets, get their specs and look for special field tyle to update
  for (widget_id, widget_data) in data['widgets'].items():
    map_widget = map_widget_html[widget_data['widget']]
    spec_widget = widget_specs[map_widget['spec']]
    # LOG.info(f'''Widget: {widget_id} -> {spec_widget['name']}  Data: {widget_data['data']}''')

    # Loop over the vars as a list, because I will be adding new ones with special value
    for (data_var, data_type) in list(widget_data['data'].items()):
      # Markdown
      # if data_type == 'markdown':
      for spec_data_pair in spec_widget['data']:
        for (spec_data_var, spec_data_type) in spec_data_pair.items():
          # If we matched the spec with our data var
          if spec_data_var == data_var:
            if spec_data_type == 'markdown':
              LOG.info(f'''Widget: {widget_id} -> {spec_widget['name']}  Markdown: {data_var} -> {spec_data_type}''')
              markdown_key = f'{spec_data_var}_html'

              # Add our custom key
              # widget_data['data'][markdown_key] = mistune.html(widget_data['data'][spec_data_var])
              # widget_data['data'][markdown_key] = widget_data['data'][markdown_key].replace('<p>', '').replace('</p>', '')
              widget_data['data'][markdown_key] = markdown(widget_data['data'][spec_data_var])


def UpdateWithEdits(edit_data, widget_data, map_widget_html, widget_specs):
  """Make changes to `data` from `edit_data`"""
  LOG.debug(f'Update with edits: {edit_data}')

  # Only needed sometimes
  result_data = {}

  edit_widget = edit_data.get('__edit_widget', None)
  edit_target = edit_data.get('__edit_target', None)
  edit_include_widget_id = edit_data.get('__edit_include_widget_id', None)

  LOG.info(f'Edit Widget: {edit_widget}  Target: {edit_target}  Include Widget ID: {edit_include_widget_id}')

  # If we are setting data
  if edit_data['__command'] == 'set':
    for key, value in edit_data.items():
      # Skip non-edit keys
      if not key.startswith('__edit.'): continue

      # Clear the edit info
      LOG.info(f'Key: {key}')
      key = key.replace('__edit.', '')

      # Split the widget and data variable name
      (widget_id, data_var) = key.split('.', 1)

      widget_data[widget_id]['data'][data_var] = value
  
  # Else, if Fetch
  elif edit_data['__command'] == 'fetch':
    result_data['__select_edit.widget_id'] = edit_data['__select_edit.widget_id']

  # Else, if Delete
  elif edit_data['__command'] == 'delete':
    LOG.info(f'Include for delete: {widget_data[edit_widget]}')
    widget_data[edit_widget]['include'][edit_target].remove(edit_include_widget_id)
    del widget_data[edit_include_widget_id]
  
  # Else, if Lower
  elif edit_data['__command'] == 'lower':
    try:
      index = widget_data[edit_widget]['include'][edit_target].index(edit_include_widget_id)
      if index < len(widget_data[edit_widget]['include'][edit_target]) - 1:
        temp = widget_data[edit_widget]['include'][edit_target][index+1]
        widget_data[edit_widget]['include'][edit_target][index+1] = widget_data[edit_widget]['include'][edit_target][index]
        widget_data[edit_widget]['include'][edit_target][index] = temp
    except ValueError as e:
      LOG.error(f'Couldnt find index lower: {edit_widget}  ID: {edit_include_widget_id}')
      return
  
  # Else, if Raise
  elif edit_data['__command'] == 'raise':
    try:
      index = widget_data[edit_widget]['include'][edit_target].index(edit_include_widget_id)
      if index > 0:
        temp = widget_data[edit_widget]['include'][edit_target][index-1]
        widget_data[edit_widget]['include'][edit_target][index-1] = widget_data[edit_widget]['include'][edit_target][index]
        widget_data[edit_widget]['include'][edit_target][index] = temp
    except ValueError as e:
      LOG.error(f'Couldnt find index raise: {edit_widget}  ID: {edit_include_widget_id}')
      return

  # Add Widget
  elif edit_data['__command'] == 'add_widget':
    include_target = edit_target # This is the name mapping between the two sides
    edit_widget_key = f'__control.add_widget.{include_target}.{edit_widget}'

    widget_label = edit_data[edit_widget_key]
    
    new_widget_data = {
      'widget': widget_label,
      'include': {
        # 'default': {},
      },
      'data':
      {
        #NOTE: Set me!
        'theme': 'parent',
      }
    }

    LOG.info(f'Widget Data before failure: Key: {edit_widget_key}  Widget Label: "{widget_label}"')

    # Set the new widget data
    widget_map_data = map_widget_html[widget_label]
    
    widget_spec = widget_specs[widget_map_data['spec']]

    # Add any includes in widget_spec to new_widget_data.include
    for include_key in widget_spec['include']:
      new_widget_data['include'][include_key] = []

    # Add default data for the widget_spec to new_widget_data.data
    for data_var_pair in widget_spec['data']:
      for (data_var_name, data_var_type) in data_var_pair.items():
        # Set Default data, if not already set
        if data_var_name not in new_widget_data['data']:
          # Dont process our meta-data (like `_source`)
          if not data_var_name.startswith('_'):
            # If we had a default set, then use that
            if '_default' in data_var_pair:
              new_widget_data['data'][data_var_name] = data_var_pair['_default']

            # Else, use the type default
            else:
              new_widget_data['data'][data_var_name] = DATA_VAR_DEFAULTS[data_var_type]#.get(data_var_type, 'parent')


            if data_var_type not in DATA_VAR_DEFAULTS:
              LOG.error(f'Missing Data Type Var default: {data_var_type}')

        # Get the var_type_data, so we can get the default
        pass  # Is this really needed?  I dont have any meta-data for this at all.  I just do it with HTML

    # Create a new Wigdet ID from UUID, and assign the new widget data into the widget data set (`data`)
    new_widget_id = utility.GetUUID()
    widget_data[new_widget_id] = new_widget_data

    # Append the new widget ID at end of our `edit_widget`s include list, so that it will append
    widget_data[edit_widget]['include'][edit_target].append(new_widget_id)

    LOG.info(f'Add Widget: New Widget Data: {new_widget_data}')
  
  return result_data


#TODO:DECOMM
def Site_Page_Example_Render(config):
  """DECOMM: Static data -- Phasing this out now -- DECOMM"""
  LOG.info(f'Input: {config.input}')

  result = utility.LoadYaml(PATH_EXAMPLE_RENDER)
  
  result['input'] = {}
  result['output'] = {}

  # Update with the 'parents'
  UpdateWidgetsWithParents(result)

  return result


def Space_Widget_Spec(config):
  """TODO:RENAME: space_widget_spec"""
  widget_spec_list = utility.LoadYaml(PATH_WIDGET_SPECS)

  result = {}

  for path in widget_spec_list:
    data = utility.LoadYaml(path)
    # LOG.info(f'Page Content path: {path}  Data: {data}')
    result[data['name']] = data
  
  return result


def Space_Map_Widget_HTML(config):
  """TODO:RENAME: space_map_widget_html"""
  result = utility.LoadYaml(PATH_MAP_WIDGET_HTML)
  
  return result



def Space_Widget_Tags(config):
  """TODO:RENAME: space_widget_tags"""
  result = utility.LoadYaml(PATH_TAGS)
  
  return result


def Site_Page(config):
  """Returns all the data for rendering an entire page.  Enforces there is at least 1 widget present."""
  result = {'uri': config.input['request']['site_page_uri'].replace('/', '.'), 'input': config.input['request'], 'time': time.time()}

  # Assume we will update the widget data from our __edit data, but if we are performing a command, we wont do that this time
  update_widget_from_edit = True
  request_command = config.input['request']['__command']

  control_widget_selected = config.input['request']['__control.widget_selected']

  # This is the widget that will be editted in the sidebar, if it doesnt exist, we set a default later
  result['edit_widget'] = config.input['stored'].get('edit_widget', None)
  if request_command != 'set':
    update_widget_from_edit = False
    LOG.debug(f'''Processing command: {config.input['request']['__command']}''')


  # If we want to select a new edit widget, do that
  if result['edit_widget'] != control_widget_selected:
    result['edit_widget'] = control_widget_selected
    # Cant use the edit data, because we just changed widgets
    update_widget_from_edit = False

  LOG.info(f'Update Widget From Edit: {update_widget_from_edit}')


  # Starting with an empty set of widgets
  result['widgets'] = config.input['stored'].get('widgets', [])
  result['widget_input'] = config.input['stored'].get('widget_input', {})
  result['edit_widget_spec'] = config.input['stored'].get('edit_widget_spec', {})
  result['widget_output'] = config.input['stored'].get('widget_output', {})


  # Remove the selected edit_widget, if we have more than 1 widget
  if request_command == 'remove' and len(result['widgets']) > 1:
    remove_widget = result.get('edit_widget', None)
    if remove_widget:
      result['edit_widget'] = None
      result['widgets'].remove(remove_widget)
      
      # Purge all Input of widget keys
      for key in list(result['widget_input'].keys()):
        if key.startswith(f'{remove_widget}.'):
          del result['widget_input'][key]

      # Purge all Output of widget keys
      for key in list(result['widget_output'].keys()):
        if key.startswith(f'{remove_widget}.'):
          del result['widget_output'][key]

  # Else, Lower the item in the widgets list.  Lower on the page
  elif request_command == 'lower':
    try:
      index = result['widgets'].index(result['edit_widget'])
      if index < len(result['widgets']) - 1:
        next_index = index + 1
        temp = result['widgets'][next_index]
        result['widgets'][next_index] = result['widgets'][index]
        result['widgets'][index] = temp
    except ValueError:
      pass

  # Else, Raise the item in the widgets list.  Raise on the page
  elif request_command == 'raise':
    try:
      index = result['widgets'].index(result['edit_widget'])
      if index > 0:
        next_index = index - 1
        temp = result['widgets'][next_index]
        result['widgets'][next_index] = result['widgets'][index]
        result['widgets'][index] = temp
    except ValueError:
      pass

  # If we dont have any widgets, or we were given an 'add' command, create one
  if len(result['widgets']) == 0 or request_command == 'add':
    # Add a new widget by UUID, can be re-ordered this way.  Floating data
    widget_uuid = utility.GetUUID()
    result['widgets'].append(widget_uuid)
    LOG.info(f''' *** Creating the first widget ***  UUID: {widget_uuid}''')

    # Thinnest input possible, we use this to render the widget_output based on the , just the type and widget_id, and we fill the rest when we get input
    widget_type_key = f'''{widget_uuid}.widget_type'''
    widget_id_key = f'''{widget_uuid}.widget_id'''
    result['widget_input'][widget_type_key] = DEFAULT_NEW_WIDGET
    result['widget_input'][widget_id_key] = widget_uuid

    # Set the edit widget to this one
    result['edit_widget'] = widget_uuid


  # If we dont have an edit_widget yet, take the first widget
  if not result['edit_widget'] or result['edit_widget'] not in result['widgets']:
    result['edit_widget'] = result['widgets'][0]


  # Render the output for all our widgets
  for widget_id in result['widgets']:
    # Get the spec for this widget
    widget_type_key = f'''{widget_id}.widget_type'''
    widget_spec = LoadWidgetData(result['widget_input'][widget_type_key])
    # widget_spec = LoadWidgetData(result['widget_input'][widget_id]['widget_type'])

    # If this is our `edit_widget`, then return the spec, as we use this to render the sidebar editor
    if widget_id == result['edit_widget']:
      result['edit_widget_spec'] = widget_spec

      # If we want to update the current edit widget with our __edit data, we do it now.  We wont do this if processing a command
      if update_widget_from_edit:
        for input_key, input_value in config.input['request'].items():
          # Skip anything that isnt from the site_page editor
          if not input_key.startswith('__edit.'): continue

          # Replace the __edit. prefix that we use generically to silo the edit variables away from any other variables, and store it as the target widget vars
          input_key = input_key.replace('__edit.', f'''{result['edit_widget']}.''', 1)
          LOG.debug(f'''Setting: widget_input:  {input_key} == {input_value}  For: {result['edit_widget']}''')
          result['widget_input'][input_key] = input_value
      
      # Else, delete all the __edit items, replace them with the current values
      else:
        # Delete all the edits for input
        for input_key in list(result['input'].keys()):
          if input_key.startswith('__edit.'):
            LOG.info(f'Found, deleting: {input_key}')
            del result['input'][input_key]
        
        # Set the edits for the new data
        for input_key, input_value in result['widget_input'].items():
          if input_key.startswith(f'''{result['edit_widget']}.'''):
            new_input_key = input_key.replace(f'''{result['edit_widget']}.''', '__edit.', 1)
            result['input'][new_input_key] = input_value


    # Simulate empty input getting processed to start out
    widget_output = ProcessInputFromSpec(config, result['widget_input'], widget_id, widget_spec)
    result['widget_output'].update(widget_output)


  return result


def LoadWidgetData(base_name, base_key=''):
  """Load our base data"""
  path = PATH_WIDGET_DATA_FORMAT.replace('{name}', base_name)

  data = utility.LoadYaml(path)

  for field_info in data:
    field = field_info['key']

    if base_key:
      new_key = f'{base_key}.{field}'
    else:
      new_key = field

    if 'import' in field_info:
      field_info['import_data'] = LoadWidgetData(field_info['import'], base_key=new_key)
      field_info['key'] = new_key

      # Give keys to all the data items, so it's easy to get their field names
      for item_data in field_info['import_data']:
        item_data['key_full'] = f'''{new_key}.{item_data['key']}'''

    elif 'list' in field_info:
      field_info['list_data'] = LoadWidgetData(field_info['list'], base_key=new_key)
      field_info['key'] = new_key

      # Give keys to all the data items, so it's easy to get their field names
      for item_data in field_info['list_data']:
        item_data['key_full'] = f'''{new_key}.{item_data['key']}'''
    
    else:
      field_info['key_full'] =  new_key

  return data


def ProcessInput_SpecificType(config, input, widget_id, spec_item, target_dict, depth=0):
  """`input_type_record` is a single spec item, with no children, that results in a single value set by `key_full` into `target_dict`
  
  `target_dict` is actually the input we are processing, thus ultimately it is our "output"
  """
  # key = widget_spec_key

  # LOG.info(f'Input: {input}')
  # LOG.debug(f'For Widget: {widget_id}  Spec Item: {spec_item}')

  # widget_edit_key = f'''__edit.{spec_item['key_full']}'''
  widget_spec_key = f'''{widget_id}.{spec_item['key_full']}'''

  # Set the raw input value in 1 place, because we need to set the default too
  raw_input_value = input.get(widget_spec_key, spec_item.get('default', ''))

  # Text
  if spec_item['type'] == 'text':
    target_dict[widget_spec_key] = raw_input_value

  # Int
  elif spec_item['type'] == 'int':
    # Lookup: Width
    if 'lookup' in spec_item and spec_item['lookup'] == 'width':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, WIDGET_WIDTH_OPTIONS, int(raw_input_value))
    
    # Lookup: Height
    elif 'lookup' in spec_item and spec_item['lookup'] == 'height':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, WIDGET_HEIGHT_OPTIONS, int(raw_input_value))
    
    # Lookup: Rounded
    elif 'lookup' in spec_item and spec_item['lookup'] == 'rounded':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, ROUNDED_OPTIONS, int(raw_input_value))
    
    # Lookup: Margin
    elif 'lookup' in spec_item and spec_item['lookup'] == 'margin':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, WIDGET_MARGIN_OPTIONS, int(raw_input_value))

    # Lookup: Bold
    elif 'lookup' in spec_item and spec_item['lookup'] == 'bold':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, BOLD_OPTIONS, int(raw_input_value))

    # Lookup: Align
    elif 'lookup' in spec_item and spec_item['lookup'] == 'text_align':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, TEXT_ALIGNMENT_OPTIONS, int(raw_input_value))

    # Lookup: Align
    elif 'lookup' in spec_item and spec_item['lookup'] == 'text_size':
      target_dict[widget_spec_key] = GetOptionByPercent(widget_spec_key, TEXT_SIZE_OPTIONS, int(raw_input_value))

    # Else, just direct assignment
    else:
      target_dict[widget_spec_key] = int(raw_input_value)

  # Checkbox
  elif spec_item['type'] == 'checkbox':
    # LOG.info(f'For Widget Checkbox: {widget_id}  Spec Item: {spec_item}')

    if raw_input_value == 'true':
      if 'value_if_true' in spec_item:
        target_dict[widget_spec_key] = spec_item['value_if_true']
      else:
        target_dict[widget_spec_key] = True
    else:
      if 'value_if_false' in spec_item:
        target_dict[widget_spec_key] = spec_item['value_if_false']
      else:
        target_dict[widget_spec_key] = False

  # Color
  elif spec_item['type'] == 'color':
    value_key = f'''{widget_spec_key}_value'''

    # Get the raw value color value, or default back to 50
    raw_color_value = input.get(value_key, DEFAULT_COLOR_VALUE)

    color_value = GetOptionByPercent(value_key, COLOR_VALUE_OPTIONS, int(raw_color_value))
    target_dict[widget_spec_key] = f'''text-{raw_input_value}-{color_value} raw-color-{raw_color_value} value-key-{value_key}'''

  # Color Background
  elif spec_item['type'] == 'color_background':
    value_key = f'''{widget_spec_key}_value'''

    # Get the raw value color value, or default back to 50
    raw_color_value = input.get(value_key, DEFAULT_COLOR_VALUE)

    color_value = GetOptionByPercent(value_key, COLOR_VALUE_OPTIONS, int(raw_color_value))
    target_dict[widget_spec_key] = f'''bg-{raw_input_value}-{color_value}'''

  # Icon
  elif spec_item['type'] == 'icon':
    target_dict[widget_spec_key] = raw_input_value

  # Unknown: Error
  else:
    LOG.error(f'''ProcessInput_SpecificType: Unknown type: {spec_item['type']}  Spec Item: {spec_item}''')


def ProcessInputFromSpec(config, input, widget_id, spec, depth=0):
  """We are given input, and we match it to the spec, so we can organize it into output"""
  result = {}

  # LOG.debug(f'Widget: {widget_id}')
  # LOG.debug(f'Input: {pprint.pformat(input)}')
  # LOG.debug(f'Spec: {pprint.pformat(spec)}')

  for spec_item in spec:
    # If this is an include of some type, then we recurse with this data as the new root item
    if 'import_data' in spec_item:
      sub_result = ProcessInputFromSpec(config, input, widget_id, spec_item['import_data'], depth=depth+1)

      result.update(sub_result)
    elif 'list_data' in spec_item:
      sub_result = ProcessInputFromSpec(config, input, widget_id, spec_item['list_data'], depth=depth+1)
      result.update(sub_result)

    # Else, this is a specific type, we process it here
    else:
      ProcessInput_SpecificType(config, input, widget_id, spec_item, result)

  return result


def Site_Editor_Dynamic(config):
  # Basic "pass-through" data
  result = {
    'widget_id': config.input['request']['widget_id'], 
    'widget_type': config.input['request']['widget_type'], 
    'input': dict(config.input['request']),
  }

  result['widget_data'] = LoadWidgetData(result['widget_type'])

  result['output'] = ProcessInputFromSpec(config, result['input'], config.input['request']['widget_id'], result['widget_data'])
  
  # Always update the widget_type
  widget_type_key = f'''{config.input['request']['widget_id']}.widget_type'''

  # Save the output result for this widget type key
  result['output'][widget_type_key] = config.input['request']['widget_type']

  if config.input:
    pass

  return result


def Site_Editor(config):
  """User performs login action on login page"""
  result = {
    'widget_id': config.input['request']['widget_id'], 
    'widget_type': config.input['request']['widget_type'], 
    'input': dict(config.input['request']),
  }




  pass  #
  uuid = '' # TDB...
  pass  ###



  if config.input:
    # We get the user request input, and the user record, which has the password
    # Verify the password is correct, and give them a token, which we will use to verify auth

    # widget_width
    var = 'widget_width'
    if config.input['request'].get(var, None): result[var] = GetOptionByPercent(var, WIDGET_WIDTH_OPTIONS, int(config.input['request'][var]))

    # widget_rounded
    var = 'widget_rounded'
    if config.input['request'].get(var, None): result[var] = GetOptionByPercent(var, ROUNDED_OPTIONS, int(config.input['request'][var]))

    # Color: Title: Background
    color_title_bg_value = GetOptionByPercent(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_background_value']))
    result['color_background'] = f'''bg-{config.input['request']['color_background']}-{color_title_bg_value}'''

    # Color: Title: Text
    color_title_text_value = GetOptionByPercent(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_text_value']))
    result['color_text'] = f'''text-{config.input['request']['color_text']}-{color_title_text_value}'''

    # widget_text_title
    var = 'widget_title'
    if config.input['request'].get(var, None): result[var] = config.input['request'][var]

    # widget_text_content
    var = 'widget_text_content'
    if config.input['request'].get(var, None): result[var] = config.input['request'][var]

    # widget_text_button
    var = 'widget_text_button'
    if config.input['request'].get(var, None): result[var] = config.input['request'][var]

    # widget_use_height
    var = 'widget_use_height'
    if config.input['request'][var] == 'true': result[var] = True
    else: result[var] = False


    # widget_height
    var = 'widget_height'
    if result['widget_use_height']:
      if config.input['request'].get(var, None): result[var] = GetOptionByPercent(var, WIDGET_HEIGHT_OPTIONS, int(config.input['request'][var]))
    else:
      result[var] = ''

  return result


def Site_Login(config):
  """User performs login action on login page"""
  username = ''

  if config.input:
    # We get the user request input, and the user record, which has the password
    # Verify the password is correct, and give them a token, which we will use to verify auth

    if config.input.get('matched', None):
      username = config.input['matched'].get('username', '')

      if config.input['request']['password'] == config.input['matched']['password']:
        result = {'username': config.input['request']['username'], 'token': utility.GetUUID(), 'authed': True}

        LOG.debug(f'\n\nCrud Test: {config.input}')
        LOG.debug(f'Result: {result}\n\n')

        return result

  # We didnt complete login, so yield no data
  failed_result = {'username': username, 'token': '', 'authed': False}
  return failed_result


def Crud_User(config):
  """"""
  if config.input:
    result = {}

    LOG.debug(f'Crud Test: {config.input}')

    output = dict(config.input['request'])
    output['_valid'] = True
    output['_error'] = None
    output['_errors'] = {}

    return output

  else:
    return None


def Transform2x(config):
  """"""
  if config.input:
    result = {}

    for key, value in config.input['mtr'].items():
      try:
        if type(value) in (float, int):
          result[key] = value * 2
      except Exception as e:
        pass

    return result
  
  else:
    return None


def Deep(config):
  """"""
  data = {
    'more': {
      'less': [5, 10, 15, 20]
    },
    'other': {
      'deeper': {
        'test': [5, 10, 99]
      },
      'again': {
        'test': [35, 50, 199]
      },
    }
  }

  return data


def Go(config):
  """"""
  data_dict = {
    '000': {'first': 'Super', 'second': 'Extreme!'},
    '001': {'first': 'Next', 'second': 'Double'},  
  }

  data_list = [
    {'id': 99, 'first': 'Super', 'second': 'Extreme!'},
    {'id': 105, 'first': 'Next', 'second': 'Double'},  
  ]

  target = '8.8.8.8'

  cmd = f'{MTR_PATH} -r -c1 {target}'
  (status, output, error) = utility.ExecuteCommand(cmd)

  mtr = ParseMTR(output, target)

  last_hop = mtr[-1]

  data = {
    'result': 'Gogogo!', 'data_dict':data_dict, 'data_list':data_list, 'mtr': mtr, 'mtr_last': last_hop, 'hop_count': len(mtr),
  }
  return data


def ParseMTR(output, target):
  """"""
  hops = []

  lines = output.split('\n')

  for line in lines[2:]:
    while '  ' in line:
      line = line.replace('  ', ' ')

    parts = line.split(' ')

    if len(parts) > 1:
      hop = {
        'index': int(parts[1].replace('.|--', '')),
        'ip': parts[2],
        'loss': float(parts[3].replace('%', '')),
        'sent': int(parts[4]),
        'last': float(parts[5]),
        'average': float(parts[6]),
        'best': float(parts[7]),
        'worst': float(parts[8]),
        'stddev': float(parts[9]),
        'target': target,  #TODO: This shouldnt be in every hop, but putting it in for now because of the table_list key specifier for link
      }

      hops.append(hop)

  return hops


def Clamp(value, clamp_min, clamp_max):
  """Clamp value between min and max values"""
  return min(clamp_max, max(clamp_min, value))


def GetOptionByPercent(name_for_error, options, value_0_100):
  """"""
  try:
    percent = value_0_100 / 100.0

    index = int(len(options) * percent)
    index = Clamp(index, 0, len(options) - 1)

    return options[index]
  except ValueError as e:
    LOG.error(f'''Site Editor: {name_for_error} input is not an integer: {value_0_100}''')
    return None
