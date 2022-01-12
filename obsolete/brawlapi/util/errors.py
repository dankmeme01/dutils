class BrawlApiError(Exception):
    pass

class BAForbidden(BrawlApiError):
    pass

class BANotFound(BrawlApiError):
    pass

class BAUnknown(BrawlApiError):
    pass

class BAInvalidIP(BAForbidden):
    def __init__(self, ip):
        super().__init__(f"This token does not allow access from IP address {ip}")