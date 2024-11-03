"""
Commands: Go
"""

import pprint

from logic import utility

from logic.log import LOG


#NOTE: On MacOS do these instructions for 0.95 or latest brew version: https://blog.dave-bell.co.uk/2020/01/06/using-mtr-on-os-x-without-sudo/
MTR_PATH = '/usr/local/bin/mtr'

WIDGET_WIDTH_OPTIONS = ['w-min', 'w-24', 'w-32', 'w-40', 'w-48', 'w-64', 'w-72', 'w-90', 'w-96', 'w-full']

WIDGET_HEIGHT_OPTIONS = ['h-min', 'h-24', 'h-32', 'h-40', 'h-48', 'h-64', 'h-72', 'h-90', 'h-96', 'h-full']

COLOR_VALUE_OPTIONS = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']

ROUNDED_OPTIONS = ['rounded-none', 'rounded-sm', 'rounded', 'rounded-md', 'rounded-lg', 'rounded-xl', 'rounded-2xl', 'rounded-full']

WIDGET_MARGIN_OPTIONS = ['m-0', 'm-2', 'm-4', 'm-6', 'm-8', 'm-12', 'm-16', 'm-24', 'm-32']

BOLD_OPTIONS = ['', 'font-thin', 'font-normal', 'font-medium', 'font-semibold', 'font-bold', 'font-extrabold', 'font-black']

# Default value for missing color_value
DEFAULT_COLOR_VALUE = 50


# Path to load different widget data type
PATH_WIDGET_DATA_FORMAT = 'data/widget_data/{name}.yaml'


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


def ProcessSpecificType(config, input, widget_id, spec_item, target_dict, depth=0):
  """`input_type_record` is a single spec item, with no children, that results in a single value set by `key_full` into `target_dict`"""
  # key = widget_spec_key

  LOG.info(f'Input: {input}')
  LOG.debug(f'For Widget: {widget_id}  Spec Item: {spec_item}')

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
      target_dict[widget_spec_key] = GetOptions(widget_spec_key, WIDGET_WIDTH_OPTIONS, int(raw_input_value))
    
    # Lookup: Height
    elif 'lookup' in spec_item and spec_item['lookup'] == 'height':
      target_dict[widget_spec_key] = GetOptions(widget_spec_key, WIDGET_HEIGHT_OPTIONS, int(raw_input_value))
    
    # Lookup: Rounded
    elif 'lookup' in spec_item and spec_item['lookup'] == 'rounded':
      target_dict[widget_spec_key] = GetOptions(widget_spec_key, ROUNDED_OPTIONS, int(raw_input_value))
    
    # Lookup: Margin
    elif 'lookup' in spec_item and spec_item['lookup'] == 'margin':
      target_dict[widget_spec_key] = GetOptions(widget_spec_key, WIDGET_MARGIN_OPTIONS, int(raw_input_value))

    # Lookup: Bold
    elif 'lookup' in spec_item and spec_item['lookup'] == 'bold':
      target_dict[widget_spec_key] = GetOptions(widget_spec_key, BOLD_OPTIONS, int(raw_input_value))

    # Else, just direct assignment
    else:
      target_dict[widget_spec_key] = int(raw_input_value)

  # Checkbox
  elif spec_item['type'] == 'checkbox':
    if raw_input_value == 'true':
      target_dict[widget_spec_key] = True
    else:
      target_dict[widget_spec_key] = False

  # Color
  elif spec_item['type'] == 'color':
    value_key = f'''{widget_spec_key}_value'''

    # Get the raw value color value, or default back to 50
    raw_color_value = input.get(value_key, DEFAULT_COLOR_VALUE)

    color_value = GetOptions(value_key, COLOR_VALUE_OPTIONS, int(raw_color_value))
    target_dict[widget_spec_key] = f'''text-{raw_input_value}-{color_value}'''

  # Color Background
  elif spec_item['type'] == 'color_background':
    value_key = f'''{widget_spec_key}_value'''

    # Get the raw value color value, or default back to 50
    raw_color_value = input.get(value_key, DEFAULT_COLOR_VALUE)

    color_value = GetOptions(value_key, COLOR_VALUE_OPTIONS, int(raw_color_value))
    target_dict[widget_spec_key] = f'''bg-{raw_input_value}-{color_value}'''

  # Icon
  elif spec_item['type'] == 'icon':
    target_dict[widget_spec_key] = raw_input_value

  # Unknown: Error
  else:
    LOG.error(f'''ProcessSpecificType: Unknown type: {spec_item['type']}  Spec Item: {spec_item}''')


def ProcessInputFromSpec(config, input, widget_id, spec, depth=0):
  """We are given input, and we match it to the spec, so we can organize it into output"""
  result = {}

  # LOG.debug(f'Spec: {pprint.pformat(spec)}')

  for spec_item in spec:
    # If this is an include of some type, then we recurse with this data as the new root item
    if 'import_data' in spec_item:
      sub_result = ProcessInputFromSpec(config, input, widget_id, spec_item['import_data'], depth+1)

      result.update(sub_result)
    elif 'list_data' in spec_item:
      sub_result = ProcessInputFromSpec(config, input, widget_id, spec_item['list_data'], depth+1)
      result.update(sub_result)

    # Else, this is a specific type, we process it here
    else:
      ProcessSpecificType(config, input, widget_id, spec_item, result)

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
    if config.input['request'].get(var, None): result[var] = GetOptions(var, WIDGET_WIDTH_OPTIONS, int(config.input['request'][var]))

    # widget_rounded
    var = 'widget_rounded'
    if config.input['request'].get(var, None): result[var] = GetOptions(var, ROUNDED_OPTIONS, int(config.input['request'][var]))

    # Color: Title: Background
    color_title_bg_value = GetOptions(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_background_value']))
    result['color_background'] = f'''bg-{config.input['request']['color_background']}-{color_title_bg_value}'''

    # Color: Title: Text
    color_title_text_value = GetOptions(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_title_value']))
    result['color_title'] = f'''text-{config.input['request']['color_title']}-{color_title_text_value}'''

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
      if config.input['request'].get(var, None): result[var] = GetOptions(var, WIDGET_HEIGHT_OPTIONS, int(config.input['request'][var]))
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


# def Site_VerifyAuth(config):
#   """"""
#   if config.input:
#     # We should have our Auth information from the Site_Login(), so now we just verify the user and token information

#     result = {'authed': False}

#     LOG.debug(f'Crud Test: {config.input}')
#     LOG.debug(f'Result: {result}')

#     return result

#   else:
#     return None


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


def GetOptions(name, options, value_0_100):
  """"""
  try:
    percent = value_0_100 / 100.0

    index = int(len(options) * percent)
    index = Clamp(index, 0, len(options) - 1)

    return options[index]
  except ValueError as e:
    LOG.error(f'''Site Editor: {name} input is not an integer: {value_0_100}''')
    return None
