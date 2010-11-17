from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django import template
import re

register = template.Library()

youtube_url_pattern = r'^(?:http://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|v/))?(?P<id>[A-Za-z0-9\-=_]{11})'
ivi_url_pattern = r'^(?:http://)?(?:www\.)?ivi\.ru/video/player/\?videoId=(?P<id>[0-9]+)'

def youtube_tag(video_id, width, height):
    return '''
    <object width="%s" height="%s">
        <param name="movie" value="http://www.youtube.com/v/%s?fs=1"></param>
        <param name="allowFullScreen" value="true"></param>
        <embed src="http://www.youtube.com/v/%s?fs=1" type="application/x-shockwave-flash" allowfullscreen="true" wmode="opaque" width="%s" height="%s"></embed>
    </object>
    ''' % (width, height, video_id, video_id, width, height)

def ivi_tag(video_id, width, height):
    return '''
    <object id="DigitalaccessVideoPlayer" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="%s" height="%s">
        <param name="movie" value="http://www.ivi.ru/video/player/?videoId=%s&_isB2C=1" />
        <param name="allowScriptAccess" value="sameDomain" />
        <param name="allowFullScreen" value="true" />
        <param name="bgcolor" value="#000000" />
        <param name="wmode" value="opaque" />
        <embed src="http://www.ivi.ru/video/player/?videoId=%s" quality="high" allowscriptaccess="sameDomain" allowfullscreen="true" wmode="opaque"  width="%s" height="%s" type="application/x-shockwave-flash"></embed>
    </object>
    ''' % (width, height, video_id, video_id, width, height)

@register.filter
@stringfilter
def youtube(url, sizes='465x278'):
    (width, height) = sizes.split('x')
    url = str(url)
    regex = re.compile(youtube_url_pattern)
    match = regex.match(url)
    if not match or not width or not height:
        return url
    video_id = match.group('id')
    video_tag = youtube_tag(video_id, width, height)
    return mark_safe(video_tag)
youtube.is_safe = True # Don't escape HTML

@register.filter
@stringfilter
def ivi(url, sizes='465x278'):
    (width, height) = sizes.split('x')
    url = str(url)
    regex = re.compile(ivi_url_pattern)
    match = regex.match(url)
    if not match or not width or not height:
        return url
    video_id = match.group('id')
    video_tag = ivi_tag(video_id, width, height)
    return mark_safe(video_tag)
ivi.is_safe = True # Don't escape HTML


# from here http://www.djangosnippets.org/snippets/212/

@register.filter
@stringfilter
def youtubize(value, sizes='425x250'):
    """
    Converts http:// links to youtube into youtube-embed statements, so that
    one can provide a simple link to a youtube video and this filter will
    embed it.

    Based on the Django urlize filter.
    """
    (width, height) = sizes.split('x')
    text = value
    # Configuration for urlize() function
    LEADING_PUNCTUATION  = ['(', '<', '&lt;']
    TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']
    word_split_re = re.compile(r'(\s+)')
    punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
            ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
            '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
    youtube_re = re.compile ('http://www.youtube.com/watch.v=(?P<videoid>(.+))')

    words = word_split_re.split(text)
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('http://www.youtube.com/watch') or middle.startswith('http://youtube.com/watch'):
                video_match = youtube_re.match(middle)
                if video_match:
                    video_id = video_match.groups()[1]
                    middle = youtube_tag(video_id, width, height)

            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return mark_safe(''.join(words))
youtubize.is_safe = True # Don't escape HTML