from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class NoFailTokenAuthentication(TokenAuthentication):
    """
    Невалидный или устаревший токен не должен ломать запрос целиком:
    пользователь просто считается анонимным. Защищённые эндпоинты
    всё равно вернут 401 из-за permissions.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None
