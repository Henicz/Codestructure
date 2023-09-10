import json
from general.output_formatting import OutputFormatting
from handlers.error_handlers import ErrorHandlers

def load_config_file(config_file):
    outputFormatting = OutputFormatting()
    print(outputFormatting.info(f"Opening file: {config_file}"))
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        ErrorHandlers.handle_io_error(e)