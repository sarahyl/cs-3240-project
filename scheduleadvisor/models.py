from django.db import models
import datetime
from django.utils.timezone import now
from django.contrib import admin
from django.contrib.auth.models import User

class Advisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=400)
    adv_name = models.CharField(max_length=200)
    email = models.CharField(max_length=100, default="")
    def __str__(self):
        return self.adv_name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=400)
    stud_name = models.CharField(max_length=200)
    comp_id = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True, default=None)
    email = models.CharField(max_length=100, default="")
    schedule_filter = models.CharField(max_length=100, default="All")


    def __str__(self):
        return self.stud_name
    def testingStudentName(self):
        return self.stud_name
    def testingStudentId(self):
        return self.comp_id
    def testingStudentMajor(self):
        return self.major

class SearchCourse(models.Model):
    subject = models.CharField(max_length=10)
    subject_description = models.CharField(max_length=200)
    catalog_number = models.IntegerField(default=0)
    title = models.CharField(max_length=200, default="")
    topic = models.CharField(max_length=400, default="")
    units = models.CharField(max_length=10)
    class_number = models.IntegerField()
    instructors = models.CharField(max_length=400)
    days = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    classroom = models.CharField(max_length=100)
    enrollment_status = models.CharField(max_length=10)
    class_capacity = models.IntegerField(default=0)
    enrollment_total = models.IntegerField(default=0)
    section_type = models.CharField(max_length=100, default="")
    acad_career_descr = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.subject + " " + str(self.catalog_number) 

class Schedule(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, default="", null=True)
    status = models.CharField(max_length=100, default="") #work in progress, pending approval, approved, rejected, enrolled
    comment = models.CharField(max_length=1000, default="")
    credits = models.CharField(max_length=10, default="0", null=True)


    def __str__(self):
        return str(self.title)

class ScheduleCourse(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=10, default="")
    subject_description = models.CharField(max_length=200, default="")
    catalog_number = models.IntegerField(default=0)
    title = models.CharField(max_length=200, default="")
    topic = models.CharField(max_length=400, default="")
    units = models.CharField(max_length=10, default="")
    class_number = models.IntegerField(default=0)
    instructors = models.CharField(max_length=400, default="")
    days = models.CharField(max_length=100, default="")
    start_time = models.CharField(max_length=100, default="")
    end_time = models.CharField(max_length=100, default="")
    classroom = models.CharField(max_length=100, default="")
    enrollment_status = models.CharField(max_length=10, default="")
    class_capacity = models.IntegerField(default=0)
    enrollment_total = models.IntegerField(default=0)
    section_type = models.CharField(max_length=100, default="")
    acad_career_descr = models.CharField(max_length=100, default="")
    
    
    def __str__(self):
        return self.subject + " " + str(self.catalog_number)
      
class Cart(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.student.username + "'s Cart"

class CartCourse(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)

    subject = models.CharField(max_length=10)
    subject_description = models.CharField(max_length=200)
    catalog_number = models.IntegerField()
    title = models.CharField(max_length=200, default="")
    topic = models.CharField(max_length=400, default="")
    units = models.CharField(max_length=10)
    class_number = models.IntegerField()
    instructors = models.CharField(max_length=400)
    days = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    end_time = models.CharField(max_length=100)
    classroom = models.CharField(max_length=100)
    enrollment_status = models.CharField(max_length=10)
    class_capacity = models.IntegerField(default=0)
    enrollment_total = models.IntegerField(default=0)
    section_type = models.CharField(max_length=100, default="")
    acad_career_descr = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.subject + " " + str(self.catalog_number)

class Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True)
    notif = models.CharField(max_length=400, default="")
    pub_date = models.DateTimeField("Time published", default=now, blank=True)
    def __str__(self):
        return self.notif

