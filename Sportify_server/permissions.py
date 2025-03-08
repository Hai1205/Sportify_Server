from rest_framework.permissions import BasePermission, SAFE_METHODS

class HasAnyPermission(BasePermission):
    """Cho phép truy cập nếu user có ít nhất một trong các quyền"""
    
    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(perm().has_permission(request, view) for perm in self.perms)

class IsArtistUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Cho phép đọc dữ liệu với mọi người dùng
        
        # Kiểm tra nếu user là artist hoặc admin
        return request.user.is_authenticated and (request.user.role == 'artist')