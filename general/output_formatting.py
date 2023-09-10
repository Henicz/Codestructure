class OutputFormatting:
    RED_TEXT = '\033[91m'
    YELLOW_TEXT = '\033[93m'
    GREEN_TEXT = '\033[92m'
    WHITE_TEXT = '\033[97m'
    RESET_TEXT = '\033[0m'

    @classmethod
    def colorize_text(cls, text, color):
        return f"{color}{text}{cls.RESET_TEXT}"
    
    @classmethod
    def error(cls, text):
        return cls.colorize_text(f"[ERROR] {text}", cls.RED_TEXT)
    
    @classmethod
    def warning(cls, text):
        return cls.colorize_text(f"[WARNING] {text}", cls.YELLOW_TEXT)
    
    @classmethod
    def valid(cls, text):
        return cls.colorize_text(f"[SUCCESS] {text}", cls.GREEN_TEXT)
    
    @classmethod
    def info(cls, text):
        return cls.colorize_text(f"[INFO] {text}", cls.WHITE_TEXT)
    
    @classmethod
    def add(cls, text):
        return cls.colorize_text(f"+ {text}", cls.GREEN_TEXT)
    
    @classmethod
    def remove(cls, text):
        return cls.colorize_text(f"- {text}", cls.RED_TEXT)
    
    @classmethod
    def change(cls, text):
        return cls.colorize_text(f"~ {text}", cls.YELLOW_TEXT)
