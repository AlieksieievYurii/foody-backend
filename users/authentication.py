from rest_framework.authentication import TokenAuthentication


class AuthenticationToken(TokenAuthentication):
    keyword: str = 'Bearer'
