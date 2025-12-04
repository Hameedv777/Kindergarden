from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import userRegistration, Student, ClassSection, Attendance, Homework, FeePayment, Fee


import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

def pay_fee(request, fee_payment_id):
    fee_payment = get_object_or_404(FeePayment, id=fee_payment_id)
    

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': int(fee_payment.fee.amount * 100),
                'product_data': {
                    'name': f"{fee_payment.student.full_name} - {fee_payment.fee.month} Fee"
                },
            },
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri(
            f"/parent/fee-success/{fee_payment.id}/"
        ),
        cancel_url=request.build_absolute_uri(
            "/parent/fee-cancel/"
        ),
    )

    fee_payment.stripe_session_id = session.id
    fee_payment.save()

    return redirect(session.url)


# def fee_success(request, fee_payment_id):
#     fee_payment = get_object_or_404(FeePayment, id=fee_payment_id)

#     fee_payment.status = "Paid"
#     fee_payment.paid_on = timezone.now()
#     fee_payment.save()

#     return render(request, "parent/fee_success.html")



# def fee_success(request, fee_payment_id):
#     if request.session.get('user_role') != 'parent':
#         return redirect('login')

#     fee_payment = FeePayment.objects.select_related(
#         'student', 'fee'
#     ).get(id=fee_payment_id)

#     return render(
#         request,
#         "parent/fee_success.html",
#         {"fee_payment": fee_payment}  # ✅ REQUIRED
#     )

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

def fee_success(request, fee_payment_id):
    if request.session.get('user_role') != 'parent':
        return redirect('login')

    fee_payment = get_object_or_404(
        FeePayment.objects.select_related('student', 'fee'),
        id=fee_payment_id,
        student__parent_id=request.session.get('user_id')  # ✅ security
    )

    # ✅ UPDATE STATUS HERE (IMPORTANT)
    if fee_payment.status != 'Paid':
        fee_payment.status = 'Paid'
        fee_payment.paid_on = timezone.now()
        fee_payment.save()

    return render(
        request,
        "parent/fee_success.html",
        {"fee_payment": fee_payment}
    )



def addFee(request):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    classes = ClassSection.objects.values_list('class_name', flat=True).distinct()

    if request.method == "POST":
        class_name = request.POST['class_name']
        month = request.POST['month']
        amount = request.POST['amount']

        # Create Fee object
        fee, created = Fee.objects.get_or_create(
            class_section=ClassSection.objects.filter(class_name=class_name).first(),
            month=month,
            defaults={'amount': amount}
        )

        # Create FeePayment for each student in that class
        students = Student.objects.filter(class_section__class_name=class_name)
        for student in students:
            FeePayment.objects.get_or_create(
                student=student,
                fee=fee,
                defaults={'status': 'Pending'}
            )

        return redirect('teacher_dashboard')

    return render(request, "teacher/add_fee.html", {"classes": classes})












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

def studentDetail(request, id):
    if request.session.get('user_role') != 'teacher':
        return redirect('login')

    student = Student.objects.select_related("parent", "class_section").get(id=id)

    return render(
        request,
        "teacher/student_detail.html",
        {"student": student}
    )



def parent_fees(request):
    if request.session.get('user_role') != 'parent':
        return redirect('login')

    parent_id = request.session.get('user_id')

    # get all students of this parent
    students = Student.objects.filter(parent_id=parent_id)

    # auto-create missing FeePayments
    for student in students:
        fees = Fee.objects.filter(class_section=student.class_section)
        for fee in fees:
            FeePayment.objects.get_or_create(
                student=student,
                fee=fee,
                defaults={'status': 'Pending'}
            )

    fee_payments = FeePayment.objects.filter(
        student__parent_id=parent_id
    ).select_related('student', 'fee')

    return render(
        request,
        "parent/fees.html",
        {"fee_payments": fee_payments}
    )


