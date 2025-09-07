from django.contrib import admin
from .models import Participant, Contest, Problem, TestCase,  Student


from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'college', 'passout_year', 'branch')
    search_fields = ('name', 'email', 'college', 'branch')
    list_filter = ('passout_year', 'branch')

    # 🚫 Prevent add/delete/change from admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# ---------- Participant Admin ----------


# ---------- Contest ----------
class ContestAdmin(admin.ModelAdmin):
    list_display = ("name", "start_at", "duration_minutes", "is_active")
admin.site.register(Contest, ContestAdmin)


# ---------- Problem ----------
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0

class ProblemAdmin(admin.ModelAdmin):
    list_display = ("contest", "code", "title", )
    inlines = [TestCaseInline]

admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase)



# ---------- Submission ----------
