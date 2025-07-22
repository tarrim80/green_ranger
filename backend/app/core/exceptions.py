class AppException(Exception):
    pass


class FileProcessingError(AppException):
    pass


class DefectTypeCreationError(AppException):
    pass


class DefectTypeUpdatingError(AppException):
    pass


class DefectTypeRemovingError(AppException):
    pass


class SurveyDefectCreationError(AppException):
    pass


class SurveyDefectUpdatingError(AppException):
    pass


class SurveyDefectRemovingError(AppException):
    pass


class SurveyCreationError(AppException):
    pass


class SurveyUpdatingError(AppException):
    pass


class SurveyRemovingError(AppException):
    pass


class SectorCreationError(AppException):
    pass


class SectorUpdatingError(AppException):
    pass


class SectorRemovingError(AppException):
    pass


class TeamCreationError(AppException):
    pass


class TeamUpdatingError(AppException):
    pass


class TeamRemovingError(AppException):
    pass


class TreeCreationError(AppException):
    pass


class TreeUpdatingError(AppException):
    pass


class TreeRemovingError(AppException):
    pass


class PhotoCreationError(AppException):
    pass


class PhotoUpdatingError(AppException):
    pass


class PhotoRemovingError(AppException):
    pass


class RoleCreationError(AppException):
    pass


class RoleUpdatingError(AppException):
    pass


class RoleRemovingError(AppException):
    pass


class NotFoundError(AppException):
    pass


class NotAllowedError(AppException):
    pass
