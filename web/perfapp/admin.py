from django.contrib import admin
from . import models

# Register your models here.

class JobAdmin(admin.ModelAdmin):
    list_display = ['owner', 'status', 'deletable']
    ordering = ['owner']
    actions=['mark_deleteable']

    def mark_deleteable(self, request, queryset):
        marked = queryset.update(deletable=True)
        if marked==1:
            msg = "1 job was"
        else:
            msg = "%s jobs were " % marked
        self.message_user(request, "%s marked for cleanup" % msg)
    mark_deleteable.short_description="Mark entries for cleanup"


admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Server)
admin.site.register(models.Attempt)
admin.site.register(models.Error)
