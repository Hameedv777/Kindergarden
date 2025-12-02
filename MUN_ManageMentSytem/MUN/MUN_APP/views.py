from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import userRegistration, Student, ClassSection, Attendance, Homework, FeePayment

def homePage(request):
    return render(request, "home.html")


# ---------------- LOGIN -----------------

def loginPage(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = userRegistration.objects.get(email=email, password=password)
        except userRegistration.DoesNotExist:
            messages.error(request, "Invalid Email or Password")
            return redirect('login')

        request.session['user_id'] = user.id
        request.session['user_role'] = user.role
        request.session['user_name'] = user.fName

        if user.role == "teacher":
            return redirect('teacher_dashboard')

        if user.role == "parent":
            return redirect('parent_dashboard')

    return render(request, "login.html")


def logoutUser(request):
    request.session.flush()
    return redirect('login')


# ---------------- TEACHER DASHBOARD -----------------

def teacherDashboard(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    name = request.session.get('user_name')
    return render(request, "teacher_dashboard.html", {"name": name})


def teacherViewStudents(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    students = Student.objects.all()
    return render(request, "teacher/students.html", {"students": students})


def teacherAttendanceSelect(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    classes = ClassSection.objects.all()
    return render(request, "teacher/attendance_select.html", {"classes": classes})


def teacherMarkAttendance(request, class_id):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    class_sec = ClassSection.objects.get(id=class_id)
    students = Student.objects.filter(class_section=class_sec)

    if request.method == "POST":
        for s in students:
            status = request.POST.get(str(s.id))
            Attendance.objects.update_or_create(
                student=s,
                date=timezone.now().date(),
                defaults={"status": status}
            )
        return redirect("teacher_dashboard")

    return render(request, "teacher/mark_attendance.html", {
        "students": students,
        "class": class_sec
    })


def uploadHomework(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    classes = ClassSection.objects.all()

    if request.method == "POST":
        class_id = request.POST["class_id"]
        title = request.POST["title"]
        desc = request.POST["description"]

        Homework.objects.create(
            class_section_id=class_id,
            title=title,
            description=desc
        )
        return redirect("teacher_dashboard")

    return render(request, "teacher/upload_homework.html", {"classes": classes})


# ---------------- PARENT DASHBOARD -----------------

def parentDashboard(request):
    if request.session.get('user_role') != 'parent':
        return redirect('login')

    name = request.session.get('user_name')
    return render(request, "parent_dashboard.html", {"name": name})


def parentChildDetails(request):
    parent_id = request.session.get('user_id')
    child = Student.objects.filter(parent_id=parent_id)
    return render(request, "parent/child_details.html", {"child": child})


def parentAttendance(request):
    parent_id = request.session.get('user_id')
    students = Student.objects.filter(parent_id=parent_id)
    attendance = Attendance.objects.filter(student__in=students)
    return render(request, "parent/attendance.html", {"attendance": attendance})


def parentFees(request):
    parent_id = request.session.get("user_id")
    students = Student.objects.filter(parent_id=parent_id)
    fees = FeePayment.objects.filter(student__in=students)
    return render(request, "parent/fee_status.html", {"fees": fees})


def parentHomework(request):
    parent_id = request.session.get("user_id")
    students = Student.objects.filter(parent_id=parent_id)
    class_list = [s.class_section_id for s in students]

    homework = Homework.objects.filter(class_section_id__in=class_list)

    return render(request, "parent/homework.html", {"homework": homework})
