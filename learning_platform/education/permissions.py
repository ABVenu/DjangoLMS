from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.user_type == 'instructor'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.user_type == 'student'

class IsAssignedToCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.userprofile.user_type == 'instructor':
            return True
        if request.user.userprofile.user_type == 'student':
            print("hello")
            return obj.course.students.filter(id=request.user.id).exists()
        return False
