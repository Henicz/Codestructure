import json
from general.output_formatting import OutputFormatting

def save_file(file_name, data):
    outputFormatting = OutputFormatting()
    try:
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(outputFormatting.error(f'Error aaa saving {file_name}: {str(e)}'))