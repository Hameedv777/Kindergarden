from django.db import models

from django.db import models
from django.utils import timezone



class userRegistration(models.Model):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )

    fName = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')

    def __str__(self):
        return self.fName
    



# -------------------------------------
# 1. CLASS & SECTION
# -------------------------------------

class ClassSection(models.Model):
    class_name = models.CharField(max_length=100)  # LKG, UKG
    section = models.CharField(max_length=10, blank=True, null=True)  # A, B, C

    def __str__(self):
        return f"{self.class_name} - {self.section}"


# -------------------------------------
# 2. STUDENT MODEL
# -------------------------------------

class Student(models.Model):
    full_name = models.CharField(max_length=200)
    dob = models.DateField()
    admission_no = models.CharField(max_length=100, unique=True)
    
    parent = models.ForeignKey(
        userRegistration,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'parent'}
    )

    class_section = models.ForeignKey(ClassSection, on_delete=models.SET_NULL, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name


# -------------------------------------
# 3. ATTENDANCE
# -------------------------------------

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=(('Present', 'Present'), ('Absent', 'Absent'))
    )

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"


# -------------------------------------
# 4. FEES / PAYMENT
# -------------------------------------

class Fee(models.Model):
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.class_section} - {self.month}"


class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)

    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    paid_on = models.DateField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=(('Paid', 'Paid'), ('Pending', 'Pending')),
        default='Pending'
    )

    def __str__(self):
        return f"{self.student.full_name} - {self.fee.month} - {self.status}"



# -------------------------------------
# 5. EVENTS
# -------------------------------------

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.title


# -------------------------------------
# 6. NOTICE BOARD
# -------------------------------------

class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_on = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

class Homework(models.Model):
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title
