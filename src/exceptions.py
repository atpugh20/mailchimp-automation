class APIError(Exception):
    """Base exception for API related errors"""
    pass

class APIConnectionError(APIError):
    """Raised when the API cannot be reached"""
    pass

class APIResponseError(APIError):
    """Raised when the API returns an unexpected response"""
    pass