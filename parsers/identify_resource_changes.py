from parsers.resolve_property_value import resolve_property_value

def identify_resource_changes(current_cst_data, state_data):
    added_count = 0
    changed_count = 0
    removed_count = 0
    resource_changes = {
        "add": [],
        "change": [],
        "remove": []
    }

    change_symbol_pointer = " --> "

    current_resource_keys = {(resource['resourceType'], resource['symbolicLink']) for resource in current_cst_data['resources']}
    state_resource_keys = {(resource['resourceType'], resource['symbolicLink']) for resource in state_data['resources']}

    for resource_key in current_resource_keys:
        if resource_key not in state_resource_keys:
            resource_type, symbolic_link = resource_key
            added_count += 1
            resource_block = next(
                (r for r in current_cst_data['resources'] if r['resourceType'] == resource_type and r['symbolicLink'] == symbolic_link),
                None
            )
            if resource_block:
                resource_changes["add"].append(resource_block)

    for resource_key in state_resource_keys:
        if resource_key not in current_resource_keys:
            resource_type, symbolic_link = resource_key
            removed_count += 1
            resource_block = next(
                (r for r in state_data['resources'] if r['resourceType'] == resource_type and r['symbolicLink'] == symbolic_link),
                None
            )
            if resource_block:
                resource_changes["remove"].append(resource_block)

    for current_resource in current_cst_data['resources']:
        symbolic_link = current_resource['symbolicLink']
        state_resource = next((r for r in state_data['resources'] if r['symbolicLink'] == symbolic_link), None)
        if state_resource:
            property_changes = []
            for key, value in current_resource['properties'].items():
                state_value = state_resource['properties'].get(key)
                resolved_value = resolve_property_value(value, state_data)
                if resolved_value != state_value:
                    changed_count += 1
                    property_changes.append(f"{key}: '{state_value}'{change_symbol_pointer}'{resolved_value}'")
            if property_changes:
                resource_type = current_resource['resourceType']
                current_resource["changedProperties"] = property_changes
                resource_changes["change"].append(current_resource)

    return added_count, changed_count, removed_count, resource_changes
