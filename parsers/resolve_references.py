from handlers.error_handlers import ErrorHandlers
from parsers.resolve_parameter_references import resolve_parameter_references
from parsers.resolve_resource_references import resolve_resource_references
from general.load_config_file import load_config_file

def resolve_references(config_file):
    try:
        config_data = load_config_file(config_file)
        resolve_parameter_references(config_data)
        resolve_resource_references(config_data)
        return config_data
    except Exception as e:
        ErrorHandlers.handle_error(e)