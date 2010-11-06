'''
>>> from utils.templatetags.utils import textile_fix_dashes
>>> textile_fix_dashes('2000-2009 2000--2009 first - second first -- second first-second :-)')
u'<p>2000&ndash;2009 2000&ndash;2009 first &mdash; second first &mdash; second first-second :-)</p>'

>>> from utils.decorators import json_success_error
>>> @json_success_error
... def success():
...     return 1
>>> print success()
Content-Type: application/json
<BLANKLINE>
{
  "success": 1
}
>>> @json_success_error(content_type='text/html')
... def error():
...     raise Exception('Error')
>>> print error()
Content-Type: text/html
<BLANKLINE>
{
  "error": "Error"
}
'''