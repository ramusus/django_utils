# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
import datetime, time

'''
DateTimeWidget using JSCal2 from http://www.dynarch.com/projects/calendar/
'''
try:
    icopath = settings.ADMIN_MEDIA_PREFIX
except:
    icopath = settings.STATIC_URL + 'admin/'

if 'grappelli' in settings.INSTALLED_APPS:
    ico_calendar = '%simg/icons/icon-datepicker.png' % icopath
    ico_cross = '%simg/icons/icon-tools-delete-handler-hover.png' % icopath
else:
    ico_calendar = '%sadmin/img/icon_calendar.gif' % icopath
    ico_cross = '%sadmin/img/icon_deletelink.gif' % icopath

class DateTimeWidget(forms.widgets.TextInput):
    input_type = 'hidden'
    class Media:
        css = {
            'all': (
                    'css/calendar/jscal2.css',
                    'css/calendar/border-radius.css',
                    'css/calendar/win2k/win2k.css',
                    )
        }
        js = (
              'js/calendar/jscal2.js',
              'js/calendar/lang/ru.js',
        )

    dformat = '%Y-%m-%d'
    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            try:
                final_attrs['value'] = \
                                   force_unicode(value.strftime(self.dformat))
            except:
                final_attrs['value'] = \
                                   force_unicode(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = u'%s_id' % (name)
        id = final_attrs['id']

        html = u'''<input%(input_attr)s />
            <span id="%(id)s_btn">
                <img src="%(ico_calendar)s" alt="%(ico_calendar_desc)s" title="%(ico_calendar_desc)s" />
                <span id="%(id)s_human_value"></span>
                <img src="%(ico_cross)s" class="ico-calendar-cross"  alt="%(ico_cross_desc)s" title="%(ico_cross_desc)s" />
            </span>
            <style>
                span#%(id)s_btn {cursor: pointer;}
                span#%(id)s_btn img {margin-right: 5px;}
                span#%(id)s_btn img.ico-calendar-cross {margin-left: 5px;}
            </style>
            %(media)s
            <script type="text/javascript">
                String.prototype.ucfirst = function() {
                    return this.substr(0, 1).toUpperCase() + this.substr(1);
                }
                String.prototype.title = function() {
                    var words = this.split(' ');
                    for(i=0; i<words.length; i++) {
                        words[i] = words[i].ucfirst();
                    }
                    return words.join(' ');
                }
                var calendar_setup = {
                    inputField: "%(id)s",
                    dateFormat: "%(jsdformat)s",
                    trigger: "%(id)s_btn",
                    onSelect: function() { this.hide() },
                    onChange: function() {
                        if(!this.selection.isEmpty()) {
                            $('#%(id)s_human_value').text(this.selection.print('%%A, %%B %%e, %%Y')[0].title());
                            $('#%(id)s_btn img.ico-calendar-cross').show();
                        } else {
                            $('#%(id)s_btn img.ico-calendar-cross').hide();
                        }
                    }
                }
                var default_date = $('#%(id)s').val().toString();
                if(default_date) {
                    calendar_setup['selection'] = new Date(default_date.substr(0,4), default_date.substr(5,2)-1, default_date.substr(8,2));
                }
                var calendar = Calendar.setup(calendar_setup);
                $('#%(id)s_btn img.ico-calendar-cross').click(function(e) {
                    e.stopPropagation();
                    calendar.selection.clear();
                    $('input#%(id)s').val('');
                    $('#%(id)s_human_value').text('');
                    $('#%(id)s_btn img.ico-calendar-cross').hide();
                    return false;
                });
            </script>''' % {
                'media': self.media,
                'input_attr': forms.util.flatatt(final_attrs),
                'id': id,
                'jsdformat': self.dformat,
                'ico_calendar': ico_calendar,
                'ico_cross': ico_cross,
                'ico_calendar_desc': _('Select date'),
                'ico_cross_desc': _('Clear date'),
            }
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        dtf = formats.get_format('DATETIME_INPUT_FORMATS')
        empty_values = forms.fields.EMPTY_VALUES

        value = data.get(name, None)
        if value in empty_values:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime(value.year, value.month, value.day)
        for format in dtf:
            try:
                return datetime.datetime(*time.strptime(value, format)[:6])
            except ValueError:
                continue
        return None

    def _has_changed(self, initial, data):
        """
        Return True if data differs from initial.
        Copy of parent's method, but modify value with strftime function before final comparsion
        """
        if data is None:
            data_value = u''
        else:
            data_value = data

        if initial is None:
            initial_value = u''
        else:
            initial_value = initial

        try:
            if force_unicode(initial_value.strftime(self.dformat)) != force_unicode(data_value.strftime(self.dformat)):
                return True
        except:
            if force_unicode(initial_value) != force_unicode(data_value):
                return True

        return False