import json
import re
from general.output_formatting import OutputFormatting
from parsers.parse_configuration_block import parse_configuration_block
from parsers.parse_resource_block import parse_resource_block
from converters.merge_parameters_blocks import merge_parameters_blocks

def convert_to_json(cst_content):
    outputFormatting = OutputFormatting()
    parsed_data = {
        "configuration": {},
        "parameters": {},
        "resources": []
    }

    try:
        config_match = re.search(r'configuration\s*{(.*?)}', cst_content, re.DOTALL)
        if config_match:
            config_block = config_match.group(1)
            parsed_data["configuration"] = parse_configuration_block(config_block)

        parameters_blocks = re.findall(r'parameters\s*{(.*?)}', cst_content, re.DOTALL)
        parsed_data["parameters"] = merge_parameters_blocks(parameters_blocks)

        resource_keys = set()

        resource_blocks = re.findall(r'resource\s+(\w+)\s+"(.*?)"\s*{(.*?)}', cst_content, re.DOTALL)
        for resource_type, symbolic_name, resource_block in resource_blocks:
            resource_data = parse_resource_block(resource_type, symbolic_name, resource_block, resource_keys)
            if resource_data == "error":
                print(outputFormatting.error(f"Duplicated resource block for resource type '{resource_type}' and symbolic link '{symbolic_name}'"))
            else:
                parsed_data["resources"].append(resource_data)

        result_json = json.dumps(parsed_data, indent=4)
        return result_json

    except Exception as e:
        print(outputFormatting.error(f"Error during JSON conversion: {str(e)}"))
        return None
