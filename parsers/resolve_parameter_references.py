def resolve_parameter_references(config_data):
    parameter_definitions = config_data.get('parameters', {})
    for resource in config_data['resources']:
        for key, value in resource['properties'].items():
            if isinstance(value, str) and value.startswith('parameter.'):
                param_name = value.split('.')[1]
                if param_name in parameter_definitions:
                    resource['properties'][key] = parameter_definitions[param_name]