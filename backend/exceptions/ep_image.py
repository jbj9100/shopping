
class ImageUploadError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ImageTypeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ImageMaxSizeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)