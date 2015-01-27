from django.contrib.admin import site, widgets
from django.utils.safestring import mark_safe
import re

class ForeignKeyRawIdReadonlyWidget(widgets.ForeignKeyRawIdWidget):
    """
    A Widget for readonly displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box.
    Option popup_choice=False remove zoom for popup window
    """
    popup_choice = True
    show_id = True

    def __init__(self, rel, popup_choice=True, show_id=True, **kwargs):
        self.popup_choice = popup_choice
        self.show_id = show_id
        kwargs['admin_site'] = site
        super(ForeignKeyRawIdReadonlyWidget, self).__init__(rel, **kwargs)

    def render(self, name, value, attrs=None):
        html = super(ForeignKeyRawIdReadonlyWidget, self).render(name, value, attrs)
        if self.show_id:
            # if dynamic inline, donor section must handle all new dynamically generated inlines
            if attrs['id'].find('__prefix__') != -1:
                script = '''<script type="text/javascript">
                    setInterval("var i=0;while($('#%(id)s').length > 0){$('#%(id)s_value').text($('#%(id)s').val());i++;}", 1000);
                </script>''' % {'id': attrs['id'].replace('__prefix__', "'+i+'")}
            else:
                script = '''<script type="text/javascript">
                    setInterval("$('#%(id)s_value').text($('#%(id)s').val());", 1000);
                </script>''' % {'id': attrs['id']}

            html = '''<span id="%(id)s_value">%(value)s</span>%(input)s%(script)s''' % {
                    'id': attrs['id'],
                    'value': value if value else '',
                    'input': html,
                    'script': script,
                }

        html = html.replace('type="text"', 'type="hidden"')
        if not self.popup_choice:
            html = re.sub(r'<a.+/a>', '', html)
        return mark_safe(html)