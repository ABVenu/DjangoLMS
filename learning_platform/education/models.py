from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='courses')
    students = models.ManyToManyField(UserProfile, related_name='enrolled_courses', blank=True)

    def __str__(self):
        return self.title

class Lecture(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lectures')

    def __str__(self):
        return self.title

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='assignments')

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    submission_date = models.DateField()

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"
