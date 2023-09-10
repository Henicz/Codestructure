import re

def parse_parameters_block(parameters_block):
    params_data = {}
    param_matches = re.findall(r'(\w+):\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))', parameters_block)
    
    for param_name, param_value, ref_value, _ in param_matches:
        if param_value:
            param_value = param_value.strip('\'"')
        elif ref_value:
            param_value = ref_value
        params_data[param_name] = param_value

    return params_data
