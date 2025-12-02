from urllib import request
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




def addStudent(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    class_sections = ClassSection.objects.all()
    parents = userRegistration.objects.filter(role='parent')

    if request.method == "POST":
        name = request.POST['name']  # Student name
        dob = request.POST['dob']    # Date of birth from form
        class_id = request.POST['class_section']
        parent_phone = request.POST['parent_phone']

        try:
            parent = userRegistration.objects.get(
                phone=parent_phone, role='parent'
            )
        except userRegistration.DoesNotExist:
            messages.error(request, "Parent phone number not found.")
            return redirect('add_student')
        
    # Generate admission number
    # -----------------------------
        last_student = Student.objects.order_by('-id').first()
        if last_student:
            last_id = last_student.id + 1
        else:
            last_id = 1

        admission_no = f"ADM{last_id:03d}"

        # Create student with DOB
        Student.objects.create(
            full_name=name,
            dob=dob,
            class_section_id=class_id,
            parent=parent,
            admission_no=admission_no
        )

        messages.success(request, "Student added successfully!")
        return redirect('teacher_dashboard')

    return render(
        request,
        "teacher/add_student.html",
        {"class_sections": class_sections, "parents": parents}
    )

