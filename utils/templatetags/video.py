from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django import template
import re
import urllib2

register = template.Library()

youtube_url_pattern = r'^(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?(?:.+)v=|v/))?(?P<id>[A-Za-z0-9\-=_]{11})'
ivi_url_pattern = r'^(?:https?://)?(?:www\.)?ivi\.ru/video/player/\?videoId=(?P<id>[0-9]+)'
kinopoisk_url_pattern = r'^(?:https?://)?(?:tr\.)?kinopoisk\.ru/(?P<id>.+)'

def youtube_tag(video_id, width, height):
    return '''
    <object width="%(width)s" height="%(height)s">
        <param name="movie" value="http://www.youtube.com/v/%(video_id)s?fs=1"></param>
        <param name="allowFullScreen" value="true"></param>
        <embed src="http://www.youtube.com/v/%(video_id)s?fs=1" type="application/x-shockwave-flash" allowfullscreen="true" wmode="opaque" width="%(width)s" height="%(height)s"></embed>
    </object>
    ''' % locals()

def ivi_tag(video_id, width, height):
    return '''
    <object id="DigitalaccessVideoPlayer" classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" width="%(width)s" height="%(height)s">
        <param name="movie" value="http://www.ivi.ru/video/player/?videoId=%video_ids&_isB2C=1"></param>
        <param name="allowScriptAccess" value="sameDomain"></param>
        <param name="allowFullScreen" value="true"></param>
        <param name="bgcolor" value="#000000"></param>
        <param name="wmode" value="opaque"></param>
        <embed src="http://www.ivi.ru/video/player/?videoId=%video_ids" quality="high" allowscriptaccess="sameDomain" allowfullscreen="true" wmode="opaque"  width="%(width)s" height="%(height)s" type="application/x-shockwave-flash"></embed>
    </object>
    ''' % locals()

def kinopoisk_tag(video_file, preview_file, video_url, width, height):

    preview_id = re.findall(r'_(\d+).jpg$', preview_file)[0]
    preview_file = 'http://tr.kinopoisk.ru/' + preview_file
    video_id = re.findall(r'^(\d+)', video_file)[0]
    video_file = re.findall(r'/(.+)', video_file)[0]
    video_file = 'http://www.kinopoisk.ru/gettrailer.php' + urllib2.quote('?trid=%s&film=%s&tid=%s' % (preview_id, video_id, video_file))

    return '''
    <object width="%(width)s" height="%(height)s">
        <param name="movie" value="http://tr.kinopoisk.ru/js/jw/player-licensed.swf"></param>
        <param name="wmode" value="transparent"></param>
        <param name="allowFullScreen" value="true"></param>
        <param name="flashVars" value="image=%(preview_file)s&%(video_url)s&file=%(video_file)s&skin=http://tr.kinopoisk.ru/js/jw/overlay.swf&controlbar=over&frontcolor=ffffff&lightcolor=ff6600&stretching=unified"></param>
        <embed src="http://tr.kinopoisk.ru/js/jw/player-licensed.swf" type="application/x-shockwave-flash" wmode="transparent" width="%(width)s" height="%(height)s" allowFullScreen="true" flashVars="image=%(preview_file)s&%(video_url)s&file=%(video_file)s&skin=http://tr.kinopoisk.ru/js/jw/overlay.swf&controlbar=over&frontcolor=ffffff&lightcolor=ff6600&stretching=unified"></embed>
    </object>
    ''' % locals()

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
    LEADING_PUNCTUATION  = ['(', '&lt;']
    TRAILING_PUNCTUATION = ['.', ',', ')', '\n', '&gt;']
    word_split_re = re.compile(r'(\s+)')
    punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
            ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
            '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
    youtube_re = re.compile('http://www.youtube.com/watch.v=(?P<videoid>([^<>]+))')

    words = word_split_re.split(text)
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.find('youtube.com') != -1:
                video_match = youtube_re.search(middle)
                if video_match:
                    video_id = video_match.groups()[1]
                    middle = '<p>%s</p>' % youtube_tag(video_id, width, height)

            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return mark_safe(''.join(words))
youtubize.is_safe = True # Don't escape HTML