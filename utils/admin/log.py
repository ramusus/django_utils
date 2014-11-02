# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.contrib.admin.models import *
from django.core.urlresolvers import reverse

def object_link(self):
    try:
        url = reverse('admin:%s_%s_change' % (self.content_type.app_label, self.content_type.model), args=(self.object_id,))
    except:
        url = False
    #TODO поставить проверку на права пользователя просмотра объекта, который смотрит
    return mark_safe(self.action_flag != DELETION and url and '<a href="%s">%s</a>' % (url, self.object_repr) or self.object_repr)
object_link.allow_tags = True
object_link.short_description = u'Объект'

def user_link(self):
    #TODO поставить проверку на права пользователя просмотра объекта, который смотрит
    return mark_safe('<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=(self.user.id,)), self.user.username))
user_link.allow_tags = True
user_link.short_description = u'Пользователь'

def action(self):
    if self.action_flag == ADDITION:
        return u'Добавление'
    elif self.action_flag == CHANGE:
        return u'Изменение'
    elif self.action_flag == DELETION:
        return u'Удаление'
action.short_description = u'Тип действия'

class LogEntryAdmin(admin.ModelAdmin):
    list_display = (user_link, object_link, 'action_time', action, 'change_message')
    list_display_links = ()
    list_filter = ['user']

admin.site.register(LogEntry, LogEntryAdmin)