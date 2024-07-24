from django.contrib import admin
from .models import UserProfile, Course, Lecture, Assignment, Submission

admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(Lecture)
admin.site.register(Assignment)
admin.site.register(Submission)
