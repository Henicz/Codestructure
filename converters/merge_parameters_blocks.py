from parsers.parse_parameters_block import parse_parameters_block

def merge_parameters_blocks(parameters_blocks):
    params_data = {}
    for parameters_block in parameters_blocks:
        params_data.update(parse_parameters_block(parameters_block))
    return params_data
