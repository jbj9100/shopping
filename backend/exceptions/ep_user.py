
class EmailAlreadyExistsError(Exception):
    def __init__(self, email: str):
        super().__init__("email already exists", email)



