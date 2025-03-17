from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.http import JsonResponse
from django.conf import settings

EXCLUDED_PATHS = ["/api/auth/login", "/api/auth/register"]
class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Bỏ qua kiểm tra token cho các URL được phép
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            return  # Cho phép request tiếp tục

        # Kiểm tra token từ header hoặc cookie
        access_token = request.COOKIES.get(settings.SIMPLE_JWT.get("COOKIE_ACCESS_TOKEN_NAME"))
        # print("access_token ", access_token)
        if "HTTP_AUTHORIZATION" not in request.META and access_token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        auth_header = request.META.get("HTTP_AUTHORIZATION", "").split()
        if len(auth_header) != 2 or auth_header[0].lower() != "bearer":
            return JsonResponse({"detail": "Invalid token format"}, status=401)

        token = auth_header[1]

        try:
            AccessToken(token)  # Kiểm tra token hợp lệ
        except Exception:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get("COOKIE_REFRESH_TOKEN_NAME"))
            if not refresh_token:
                return JsonResponse({"detail": "Authentication required"}, status=401)

            try:
                new_access_token = str(RefreshToken(refresh_token).access_token)
                response = JsonResponse({"detail": "Token refreshed"})
                response.set_cookie(
                    settings.SIMPLE_JWT.get("COOKIE_ACCESS_TOKEN_NAME"),
                    new_access_token,
                    httponly=True,
                    secure=True,
                    samesite="Lax"
                )
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {new_access_token}"
                return response
            except Exception:
                return JsonResponse({"detail": "Session expired, please log in again"}, status=401)

