from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django import template
import re

register = template.Library()

youtube_url_pattern = r'^(?:http://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|v/))?(?P<id>[A-Za-z0-9\-=_]{11})'

def youtube_tag(video_id, width, height):
    return '''
    <object width="%s" height="%s">
        <param name="movie" value="http://www.youtube.com/v/%s"></param>
        <param name="allowFullScreen" value="true"></param>
        <embed src="http://www.youtube.com/v/%s" type="application/x-shockwave-flash" allowfullscreen="true" wmode="opaque" width="%s" height="%s"></embed>
    </object>
    ''' % (width, height, video_id, video_id, width, height)

@register.filter
@stringfilter
def youtube(url, sizes='465x278'):
    [(width, height)] = re.findall(r'^(.+)x(.+)$', sizes)
    url = str(url)
    regex = re.compile(youtube_url_pattern)
    match = regex.match(url)
    if not match or not width or not height:
        return ''
    video_id = match.group('id')
    video_tag = youtube_tag(video_id, width, height)
    return mark_safe(video_tag)
youtube.is_safe = True # Don't escape HTML