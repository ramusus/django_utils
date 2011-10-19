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

>>> from django.db import models
>>> from utils.models import ModelNameFormCases
>>> class MyModel(models.Model, ModelNameFormCases):
...     class Meta:
...         verbose_name = 'verbose_name'
...     class VerboseNameFormCases:
...         plural = 'plural_form'
...         cases = '1case,2case,3case,4case,5case,6case'
>>> MyModel.verbose_name_form('genitive')
u'2case'
>>> MyModel.verbose_name_form('about')
u'6case'
>>> MyModel.verbose_name_form('plural')
u'plural_form'
>>> MyModel.verbose_name_form('error')
u'verbose_name'
'''