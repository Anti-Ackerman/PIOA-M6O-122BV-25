class DatabaseError(Exception):
    pass

class TableNotFoundError(DatabaseError):
    pass

class TableAlreadyExistsError(DatabaseError):
    pass

class InvalidStorageDataError(DatabaseError):
    pass