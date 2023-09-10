def resolve_property_value(value, state_data):
    if isinstance(value, str) and value.startswith('parameter.'):
        param_name = value.split('.')[1]
        return state_data['parameters'].get(param_name, value)
    elif isinstance(value, str) and value.startswith('resource.'):
        parts = value.split('.')
        if len(parts) == 4:
            resource_name, resource_attr = parts[2], parts[3]
            resource = next((r for r in state_data['resources'] if r['symbolicLink'] == resource_name), None)
            if resource:
                return resource['properties'].get(resource_attr, value)
    return value