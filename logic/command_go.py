

from logic import utility

from logic.log import LOG


#NOTE: On MacOS do these instructions for 0.95 or latest brew version: https://blog.dave-bell.co.uk/2020/01/06/using-mtr-on-os-x-without-sudo/
MTR_PATH = '/usr/local/bin/mtr'

WIDGET_WIDTH_OPTIONS = ['w-min', 'w-24', 'w-32', 'w-40', 'w-48', 'w-64', 'w-72', 'w-90', 'w-96', 'w-full']

HEIGHT_WIDTH_OPTIONS = ['h-min', 'h-24', 'h-32', 'h-40', 'h-48', 'h-64', 'h-72', 'h-90', 'h-96', 'h-full']

COLOR_VALUE_OPTIONS = ['50', '100', '200', '300', '400', '500', '600', '700', '800', '900']

ROUNDED_OPTIONS = ['rounded-none', 'rounded-sm', 'rounded', 'rounded-md', 'rounded-lg', 'rounded-xl', 'rounded-2xl', 'rounded-full']

# Path to load different widget data type
PATH_WIDGET_DATA_FORMAT = 'data/widget_data/{name}.yaml'


def LoadWidgetData(base_name):
  """Load our base data"""
  path = PATH_WIDGET_DATA_FORMAT.replace('{name}', base_name)

  data = utility.LoadYaml(path)

  for (field, field_info) in data.items():
    if 'import' in field_info:
      field_info['data'] = LoadWidgetData(field_info['import'])

    elif 'list' in field_info:
      field_info['list_data'] = LoadWidgetData(field_info['list'])


  return data


def Site_Editor_Dynamic(config):
  result = {
    'widget_id': config.input['request']['widget_id'], 
    'widget_type': config.input['request']['widget_type'], 
    # 'input': dict(config.input['request']),
  }

  result['widget_data'] = LoadWidgetData(result['widget_type'])

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
    color_title_bg_value = GetOptions(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_title_background_value']))
    result['color_title_background'] = f'''bg-{config.input['request']['color_title_background']}-{color_title_bg_value}'''

    # Color: Title: Text
    color_title_text_value = GetOptions(var, COLOR_VALUE_OPTIONS, int(config.input['request']['color_title_text_value']))
    result['color_title_text'] = f'''text-{config.input['request']['color_title_text']}-{color_title_text_value}'''

    # widget_text_title
    var = 'widget_text_title'
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
      if config.input['request'].get(var, None): result[var] = GetOptions(var, HEIGHT_WIDTH_OPTIONS, int(config.input['request'][var]))
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
