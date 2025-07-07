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


class SectorCreationError(AppException):
    pass


class SectorRemovingError(AppException):
    pass


class TeamCreationError(AppException):
    pass


class TeamRemovingError(AppException):
    pass


class TreeCreationError(AppException):
    pass


class TreeRemovingError(AppException):
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


class NotAllowedError(AppException):
    pass
