import json
from general.output_formatting import OutputFormatting

def load_state_file(state_file_name):
    outputFormatting = OutputFormatting()
    try:
        with open(state_file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(outputFormatting.error(f"State file '{state_file_name}' not found. Ensure you have run 'codestructure read' before 'plan'."))
        return None