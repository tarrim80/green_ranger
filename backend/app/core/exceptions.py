class AppException(Exception):
    pass


class FileProcessingError(AppException):
    pass


class DefectTypeCreationError(AppException):
    pass


class SurveyDefectCreationError(AppException):
    pass


class SurveyCreationError(AppException):
    pass


class PhotoCreationError(AppException):
    pass


class PhotoRemovingError(AppException):
    pass


class NotFoundError(AppException):
    pass
