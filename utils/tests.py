'''
>>> from utils.templatetags.utils import textile_fix_dashes
>>> textile_fix_dashes('2000-2009 2000--2009 first - second first -- second first-second :-)')
u'<p>2000&ndash;2009 2000&ndash;2009 first &mdash; second first &mdash; second first-second :-)</p>'
'''