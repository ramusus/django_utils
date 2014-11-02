# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.admin.widgets import AdminFileWidget
from django.forms.widgets import Widget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from PIL import Image
import os

image_default_width = 100
image_default_height = 50
video_default_width = 250
video_default_height = 150

def thumbnail(image_path, width=False, height=False):
    width = int(width) or image_default_width
    height = int(height) or image_default_height

    try:
        from sorl.thumbnail.main import DjangoThumbnail
        t = DjangoThumbnail(relative_source=image_path, requested_size=(width,height))
        return u'<img src="%s" alt="%s" />' % (t.absolute_url, image_path)
    except IOError:
        return 'IOError'
    except ImportError:
        absolute_url = os.path.join(settings.MEDIA_ROOT, image_path)
        return u'<img src="%s" alt="%s" />' % (absolute_url, image_path)

class AdminImageAbstract(AdminFileWidget):
    def __init__(self, width=False, height=False, *args, **kwargs):
        self.width = int(width) or image_default_width
        self.height = int(height) or image_default_height
        super(AdminImageAbstract, self).__init__(*args, **kwargs)

class AdminImageWidget(AdminImageAbstract):
    '''
    A FileField Widget that displays an image instead of a file path
    if the current file is an image.
    '''
    def render(self, name, value, attrs=None):
        output = []
        file_name = str(value)
        if file_name:
            file_path = '%s%s' % (settings.MEDIA_URL, file_name)
            try:            # is image
                Image.open(os.path.join(settings.MEDIA_ROOT, file_name))
                output.append('<a target="_blank" href="%s">%s</a><br />%s <a target="_blank" href="%s">%s</a><br />%s ' % \
                    (file_path, thumbnail(file_name, self.width, self.height), _('Currently:'), file_path, file_name, _('Change:')))
            except IOError: # not image
                output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                    (_('Currently:'), file_path, file_name, _('Change:')))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class AdminImagePreviewWidget(Widget):
    '''
    A FileField Widget for only previewing image
    '''
    def __init__(self, width=False, height=False, *args, **kwargs):
        self.width = int(width) or image_default_width
        self.height = int(height) or image_default_height
        super(AdminImagePreviewWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = []
        if value:
            file_name = str(value)
            file_path = '%s%s' % (settings.MEDIA_URL, file_name)
            try:            # is image
                Image.open(os.path.join(settings.MEDIA_ROOT, file_name))
                output.append('''
                    <input type="hidden" name="%s" value="%s" />
                    <a target="_blank" href="%s">%s</a>
                    ''' % (name, value, file_path, thumbnail(file_name, self.width, self.height)))
            except IOError: # not image
                output.append('<input type="text" name="%s" />' % name)
        else:
            output.append('<input type="text" name="%s" />' % name)

        return mark_safe(u''.join(output))

class AdminVideoPreviewWidget(Widget):
    '''
    A FileField Widget for only previewing image
    '''
    def __init__(self, width=False, height=False, *args, **kwargs):
        self.width = int(width) or video_default_width
        self.height = int(height) or video_default_height
        super(AdminVideoPreviewWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        output = []
        if value:
            output.append('''
                <input type="hidden" name="%s" value="%s" />
                <object width="%d" height="%d">
                    <param name="movie" value="http://www.youtube.com/v/%s"></param>
                    <param name="allowFullScreen" value="true"></param>
                    <embed src="http://www.youtube.com/v/%s" type="application/x-shockwave-flash" allowfullscreen="true" width="%d" height="%d"></embed>
                </object>
                ''' % (name, value, self.width, self.height, value, value, self.width, self.height))
        else:
            output.append('<input type="text" name="%s" />' % name)

        return mark_safe(u''.join(output))