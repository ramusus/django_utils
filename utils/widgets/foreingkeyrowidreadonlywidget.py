from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe
import re

class ForeignKeyRawIdReadonlyWidget(ForeignKeyRawIdWidget):
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
        super(ForeignKeyRawIdReadonlyWidget, self).__init__(rel, **kwargs)

    def render(self, name, value, attrs=None):
        html = super(ForeignKeyRawIdReadonlyWidget, self).render(name, value, attrs)
        #TODO Invent how show id in span, when value is returned from popup. onchange doesn't work at all
        if not self.show_id:
            html = html.replace('type="text"', 'type="hidden"')
        else:
            html = html.replace('<input', '<input readonly')
        if not self.popup_choice:
            html = re.sub(r'<a.+/a>', '', html)
        return mark_safe(html)