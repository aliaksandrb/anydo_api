class Error(Exception): pass

class ClientError(Error): pass

class UnauthorizedError(ClientError): pass
class BadRequestError(ClientError): pass
class InternalServerError(ClientError): pass
class ConflictError(ClientError): pass

