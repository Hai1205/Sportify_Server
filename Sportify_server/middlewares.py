from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

EXCLUDED_PATHS = ["/api/auth/login", "/api/auth/register"]

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # print(f"Middleware: Đang kiểm tra {request.path}")

        # Bỏ qua xác thực cho các URL trong danh sách EXCLUDED_PATHS
        if any(request.path.startswith(path) for path in EXCLUDED_PATHS):
            # print("Middleware: Bỏ qua xác thực do URL trong danh sách EXCLUDED_PATHS")
            return None  

        # Kiểm tra xem view có `AllowAny` không
        view_class = getattr(view_func, 'view_class', None)
        if view_class:
            # print(f"Middleware: Kiểm tra quyền hạn của {view_class.__name__}")

            if hasattr(view_class, 'permission_classes'):
                # print(f"Middleware: Các quyền của view: {view_class.permission_classes}")

                if AllowAny in view_class.permission_classes:
                    # print("Middleware: Bỏ qua xác thực do có AllowAny")
                    return None  # Không yêu cầu xác thực

        # Kiểm tra token
        access_token = request.COOKIES.get(settings.SIMPLE_JWT.get("COOKIE_ACCESS_TOKEN_NAME"))
        if "HTTP_AUTHORIZATION" not in request.META and access_token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"

        auth_header = request.META.get("HTTP_AUTHORIZATION", "").split()
        if len(auth_header) != 2 or auth_header[0].lower() != "bearer":
            # print("Middleware: Token không hợp lệ hoặc không có")
            return JsonResponse({"detail": "Invalid token format"}, status=401)

        token = auth_header[1]

        try:
            AccessToken(token)  # Kiểm tra token hợp lệ
        except Exception:
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT.get("COOKIE_REFRESH_TOKEN_NAME"))
            if not refresh_token:
                # print("Middleware: Không có refresh token -> Yêu cầu đăng nhập")
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
                # print("Middleware: Token được refresh")
                return response
            except Exception:
                # print("Middleware: Refresh token không hợp lệ")
                return JsonResponse({"detail": "Session expired, please log in again"}, status=401)

        # print("Middleware: Xác thực thành công, tiếp tục request")
        return None  # Tiếp tục request nếu không có lỗi
