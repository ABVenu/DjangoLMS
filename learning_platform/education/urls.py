from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    RegisterView, LoginView, CourseListCreate, CourseDetail,
    LectureListCreate, LectureDetail, AssignmentListCreate,
    AssignmentDetail, SubmissionListCreate, SubmissionDetail,
    AssignStudentToCourse, RemoveStudentFromCourse
)

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],  # Ensure this is a list or tuple
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    path('courses/', CourseListCreate.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetail.as_view(), name='course-detail'),
    
    path('lectures/', LectureListCreate.as_view(), name='lecture-list-create'),
    path('lectures/<int:pk>/', LectureDetail.as_view(), name='lecture-detail'),
    
    path('courses/<int:pk>/assign-student/', AssignStudentToCourse.as_view(), name='assign-student-to-course'),
    path('courses/<int:pk>/remove-student/', RemoveStudentFromCourse.as_view(), name='remove-student-from-course'),
    
    path('assignments/', AssignmentListCreate.as_view(), name='assignment-list-create'),
    path('assignments/<int:pk>/', AssignmentDetail.as_view(), name='assignment-detail'),
    
    path('submissions/', SubmissionListCreate.as_view(), name='submission-list-create'),
    path('submissions/<int:pk>/', SubmissionDetail.as_view(), name='submission-detail'),
    
    # Swagger and ReDoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
