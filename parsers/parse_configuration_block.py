import re
from general.output_formatting import OutputFormatting

def parse_configuration_block(config_block):
    config_data = {}
    config_lines = config_block.split('\n')
    outputFormatting = OutputFormatting()

    allowed_attributes = set(["subscription_id", "spn_object_id", "spn_secret", "state_file_name", "tenant_id"])
    unwanted_attributes = set()

    for line in config_lines:
        matches = re.findall(r'(\w+):\s*("(.*?)"|(\'[^\']*\'|"[^"]*"))', line)
        for match in matches:
            attribute = match[0]
            if attribute in allowed_attributes:
                config_data[attribute] = match[1].strip('\'"')
            elif attribute not in unwanted_attributes:
                unwanted_attributes.add(attribute)

    for attribute in unwanted_attributes:
        print(outputFormatting.warning(f"Unwanted configuration attribute found: {attribute}"))

    return config_data