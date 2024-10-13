

from logic import utility


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

	cmd = f'mtr -r -c1 {target}'
	(status, output, error) = utility.ExecuteCommand(cmd)

	mtr = ParseMTR(output, target)

	last_hop = mtr[-1]

	data = {
		'result': 'Gogogog!', 'data_dict':data_dict, 'data_list':data_list, 'mtr': mtr, 'mtr_last': last_hop, 'hop_count': len(mtr),
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
				'target': target,	#TODO: This shouldnt be in every hop, but putting it in for now because of the table_list key specifier for link
			}

			hops.append(hop)

	return hops


