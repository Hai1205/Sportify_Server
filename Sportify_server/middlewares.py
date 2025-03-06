from django.utils.deprecation import MiddlewareMixin

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "HTTP_AUTHORIZATION" not in request.META:  # Nếu chưa có token
            access_token = request.COOKIES.get("access_token")
            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
