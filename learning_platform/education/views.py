from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Course, Lecture, Assignment, Submission,UserProfile
from .serializers import CourseSerializer, LectureSerializer, AssignmentSerializer, SubmissionSerializer,UserProfileSerializer
from .permissions import IsInstructor, IsStudent, IsAssignedToCourse
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework_simplejwt.settings import api_settings
from drf_yasg.utils import swagger_auto_schema

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = UserProfile(user=user,user_type=request.data['user_type'])
            profile.save()
            return Response({'message': 'User registered successfully', 'user': UserSerializer(user).data, 'profile':UserProfileSerializer(profile).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
            
            # Set tokens as HttpOnly cookies
            response.set_cookie(
                'refresh_token', str(refresh),
                httponly=True,
                secure=False
            )
            response.set_cookie(
                'access_token', str(refresh.access_token),
                httponly=True,
                secure=False
            )
            
            return response
        
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CourseListCreate(APIView):
    """
    List all courses or create a new course.
    """
    permission_classes = [IsInstructor]
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user.userprofile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetail(APIView):
    permission_classes = [IsInstructor]

    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        course = Course.objects.get(pk=pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LectureListCreate(APIView):
    """
    List all lectures or create a new lecture.
    """
    permission_classes = [IsInstructor]
    @swagger_auto_schema(
        operation_description="Retrieve a list of all lecture",
        security=[{'Bearer': []}],
        responses={200: LectureSerializer(many=True)},
    )
    def get(self, request):
        """
        Return a list of all lectures.
        """
        lectures = Lecture.objects.all()
        serializer = LectureSerializer(lectures, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Create a new lecture",
        security=[{'Bearer': []}],
        request_body=LectureSerializer,
        responses={201: LectureSerializer},
    )
    def post(self, request):
        print("form view", request.user)
        serializer = LectureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LectureDetail(APIView):
    permission_classes = [IsInstructor, IsAssignedToCourse]

    def get(self, request, pk):
        lecture = Lecture.objects.get(pk=pk)
        serializer = LectureSerializer(lecture)
        return Response(serializer.data)

    def put(self, request, pk):
        lecture = Lecture.objects.get(pk=pk)
        serializer = LectureSerializer(lecture, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        lecture = Lecture.objects.get(pk=pk)
        lecture.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AssignmentListCreate(APIView):
    permission_classes = [IsInstructor]

    def get(self, request):
        assignments = Assignment.objects.all()
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentDetail(APIView):
    permission_classes = [IsInstructor]

    def get(self, request, pk):
        assignment = Assignment.objects.get(pk=pk)
        serializer = AssignmentSerializer(assignment)
        return Response(serializer.data)

    def put(self, request, pk):
        assignment = Assignment.objects.get(pk=pk)
        serializer = AssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        assignment = Assignment.objects.get(pk=pk)
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SubmissionListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.userprofile.user_type == 'instructor':
            submissions = Submission.objects.all()
        else:
            submissions = Submission.objects.filter(student=request.user.userprofile)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.userprofile.user_type != 'student':
            return Response({'error': 'Only students can submit assignments'}, status=status.HTTP_403_FORBIDDEN)

        # Check for missing assignment ID
        assignment_id = request.data.get('assignment')
        if not assignment_id:
            return Response({'error': 'Assignment ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response({'error': 'Invalid Assignment ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the submission
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user.userprofile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubmissionDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        submission = Submission.objects.get(pk=pk)
        if request.user.userprofile.user_type == 'student' and submission.student != request.user.userprofile:
            return Response({'error': 'Not allowed to view this submission'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SubmissionSerializer(submission)
        return Response(serializer.data)

    def put(self, request, pk):
        submission = Submission.objects.get(pk=pk)
        if request.user.userprofile.user_type == 'student' and submission.student != request.user.userprofile:
            return Response({'error': 'Not allowed to edit this submission'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SubmissionSerializer(submission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        submission = Submission.objects.get(pk=pk)
        if request.user.userprofile.user_type == 'student' and submission.student != request.user.userprofile:
            return Response({'error': 'Not allowed to delete this submission'}, status=status.HTTP_403_FORBIDDEN)
        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AssignStudentToCourse(APIView):
    permission_classes = [IsInstructor]

    def post(self, request, pk):
        course = Course.objects.get(pk=pk)
        student_ids = request.data.get('students')  # List of student IDs to assign

        if not student_ids:
            return Response({'error': 'No student IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        students = UserProfile.objects.filter(id__in=student_ids)
        if students.count() != len(student_ids):
            return Response({'error': 'One or more student IDs are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        course.students.set(students)  # Assign students to the course
        course.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RemoveStudentFromCourse(APIView):
    permission_classes = [IsInstructor]

    def post(self, request, pk):
        course = Course.objects.get(pk=pk)
        student_id = request.data.get('student')  # Single student ID to remove

        if not student_id:
            return Response({'error': 'No student ID provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = UserProfile.objects.get(id=student_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Student ID is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        course.students.remove(student)  # Remove student from the course
        course.save()
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)