import re

class CustomError(Exception):
    """Base class for custom exceptions."""
    pass

class RateLimitError(CustomError):
    """Specific error related to a particular operation."""
    def __init__(self, message, error_code=403):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.wait_time = self.__extract_wait_time__(message)

    def __str__(self):
        if self.error_code:
            return f"SpecificError (Code: {self.error_code}): {self.message}"
        else:
            return f"SpecificError: {self.message}"        
    
    
    def __extract_wait_time__(self, api_response):
        """Extracts wait time from the API response string."""
        match = re.search(r"API Token Busy: (\d+\.?\d*) seconds remaining", api_response)
        if match:
            return float(match.group(1))
        else:
            return 5  # Default wait time if extraction fails