from django.contrib import admin
from .models import Message, UserInfo


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ("pub_date", )


# Register your models here.
admin.site.register(Message, MessageAdmin)
admin.site.register(UserInfo)
