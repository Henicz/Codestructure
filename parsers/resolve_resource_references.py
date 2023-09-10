def resolve_resource_references(config_data):
    resource_definitions = {resource['symbolicLink']: resource for resource in config_data['resources']}
    for resource in config_data['resources']:
        for key, value in resource['properties'].items():
            if isinstance(value, str) and value.startswith('resource.'):
                parts = value.split('.')
                if len(parts) == 4:
                    resource_name, resource_attr = parts[2], parts[3]
                    if resource_name in resource_definitions and resource_attr in resource_definitions[resource_name]['properties']:
                        resource['properties'][key] = resource_definitions[resource_name]['properties'][resource_attr]
