from django.contrib import admin
from .models import userRegistration, ClassSection,Student, Fee

class UserAdmin(admin.ModelAdmin):
    list_display = ("fName", "email", "phone", "role")
    list_filter = ("role",)
    search_fields = ("fName", "email")

admin.site.register(userRegistration, UserAdmin)


admin.site.register(ClassSection)
admin.site.register(Student)
admin.site.register(Fee)
