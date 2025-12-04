from django.urls import path
from . import views

urlpatterns = [

    path("", views.homePage, name="home"),  # 👈 Home page
    path("login/", views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),

    path('teacher/dashboard/', views.teacherDashboard, name="teacher_dashboard"),
    path('parent/dashboard/', views.parentDashboard, name="parent_dashboard"),

    # path("register/teacher/", views.registerTeacher, name="register_teacher"),
    # path("register/parent/", views.registerParent, name="register_parent"),

    # Teacher Features
    path("teacher/students/", views.teacherViewStudents, name="teacher_view_students"),
    path("teacher/attendance/", views.teacherAttendanceSelect, name="attendance_select"),
    path("teacher/attendance/mark/<int:class_id>/", views.teacherMarkAttendance, name="mark_attendance"),
    path("teacher/homework/", views.uploadHomework, name="upload_homework"),

    path('parent/dashboard/', views.parentDashboard, name="parent_dashboard"),
    path("parent/child/", views.parentChildDetails, name="parent_child"),
    path("parent/attendance/", views.parentAttendance, name="parent_attendance"),
    path("parent/fees/", views.parentFees, name="parent_fees"),
    path("parent/homework/", views.parentHomework, name="parent_homework"),

    path('teacher/add-student/', views.addStudent, name='add_student'),
    path("teacher/student/<int:id>/", views.studentDetail, name="student_detail"),

    path("parent/pay/<int:fee_payment_id>/", views.pay_fee, name="pay_fee"),
    path("parent/fee-success/<int:fee_payment_id>/",views.fee_success,name="fee_success"),

    path('teacher/add-fee/', views.addFee, name='add_fee'),





]