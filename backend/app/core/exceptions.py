from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "权限不足"):
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)


class BadRequestException(AppException):
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)
