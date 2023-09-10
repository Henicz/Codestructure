from general.output_formatting import OutputFormatting

class ErrorHandlers:
    @staticmethod
    def handle_io_error(e):
        outputFormatting = OutputFormatting()
        return outputFormatting.error(f"An I/O error occurred: {str(e)}")

    @staticmethod
    def handle_json_error(e):
        outputFormatting = OutputFormatting()
        return outputFormatting.error(f"A JSON error occurred: {str(e)}")

    @staticmethod
    def handle_regex_error(e):
        outputFormatting = OutputFormatting()
        return outputFormatting.error(f"A regular expression error occurred: {str(e)}")

    @staticmethod
    def handle_unexpected_error(e):
        outputFormatting = OutputFormatting()
        return outputFormatting.error(f"An unexpected error occurred: {str(e)}")
