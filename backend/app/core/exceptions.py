class AppException(Exception):
    pass


class FileProcessingError(AppException):
    pass


class DefectTypeCreationError(AppException):
    pass


class DefectTypeRemovingError(AppException):
    pass


class SurveyDefectCreationError(AppException):
    pass


class SurveyDefectRemovingError(AppException):
    pass


class SurveyCreationError(AppException):
    pass


class SurveyRemovingError(AppException):
    pass


class PhotoCreationError(AppException):
    pass


class PhotoRemovingError(AppException):
    pass


class RoleCreationError(AppException):
    pass


class RoleRemovingError(AppException):
    pass


class NotFoundError(AppException):
    pass
