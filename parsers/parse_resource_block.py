import re
from general.output_formatting import OutputFormatting

outputFormatting = OutputFormatting()

resource_config = {
    "resource_group": {
        "name": r'name:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))',
        "location": r'location:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))'
    },
    "storage_account": {
        "name": r'name:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))',
        "location": r'location:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))',
        "resource_group_name": r'resource_group_name:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))',
        "sku": r'sku:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))',
        "kind": r'kind:\s*((\'[^\']*\'|"[^"]*")|(\w+(?:\.\w+)*))'
    }
}

def parse_resource_block(resource_type, symbolic_name, resource_block, resource_keys):
    resource_key = (resource_type, symbolic_name)
    error_message = "error"
    
    if resource_key in resource_keys:
        return error_message
    else:
        resource_keys.add(resource_key)
        
        resource_data = {
            "resourceType": resource_type,
            "symbolicLink": symbolic_name,
            "properties": {}
        }

        if resource_type in resource_config:
            for param_name, param_pattern in resource_config[resource_type].items():
                param_match = re.search(param_pattern, resource_block)
                if param_match:
                    resource_data["properties"][param_name] = param_match.group(1).strip('\'"')

        return resource_data
