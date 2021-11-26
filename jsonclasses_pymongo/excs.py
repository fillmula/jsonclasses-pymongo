class DatabaseNotConnectedException(Exception):
    """This exception is raised when collection is accessed however database is
    not connected.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
