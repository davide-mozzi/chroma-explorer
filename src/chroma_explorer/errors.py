class ArgumentError(Exception):
    """Error with the arguments passed to the application at launch"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MissingPathError(ArgumentError):
    """No path argument was passed to the application"""


class EmptyDirectoryError(ArgumentError):
    """The path passed as argument to the application is an empty directory"""


class NonExistentPathError(ArgumentError):
    """The path passed as argument to the application does not exist"""


class InvalidPathError(ArgumentError):
    """The path passed as argument to the applicaiton is not a valid ChromaDB directory,
    nor an empty/non-existent one."""
