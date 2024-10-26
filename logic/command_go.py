

from logic import utility

from logic.log import LOG


#NOTE: On MacOS do these instructions for 0.95 or latest brew version: https://blog.dave-bell.co.uk/2020/01/06/using-mtr-on-os-x-without-sudo/
MTR_PATH = '/usr/local/bin/mtr'


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


