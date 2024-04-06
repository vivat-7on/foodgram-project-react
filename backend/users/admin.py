from django.contrib import admin

from .models import CustomUser, Subscribe

admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'Foodgram'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'date_joined',
        'is_staff',
        'is_superuser',
    )
    list_display_links = ('email', 'username')
    ordering = ('date_joined', 'username')
    list_filter = ('email', 'username')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'subscribed_to')
    list_display_links = ('subscriber', 'subscribed_to')
    ordering = ('subscriber', 'subscribed_to')
    list_filter = ('subscriber', 'subscribed_to')



