class BrawlAPIException(Exception):
    pass

class AlreadyInitialized(BrawlAPIException):
    pass

class NotInitialized(BrawlAPIException):
    pass