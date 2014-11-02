'''
from here http://www.djangosnippets.org/snippets/1648/
Added media:group support
'''

"""feedgenerator.py
Provides basic Feed implementation for generating a MediaRSS feed for photologue galleries

Sample usage (in urls.py):

from feedgenerator import PhotologueFeed

class MyPhotoFeed(PhotologueFeed):
    title = 'My Photologue Galleries'
    description = 'Latest updates to My Photologue Galleries'
    title_template = 'feeds/gallery_feed_title.html'
    description_template = 'feeds/gallery_feed_description.html'

photofeeds = {
    'gallery': MyPhotoFeed,
}

urlpatterns += patterns('',
    url(r'^photologue/feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': photofeeds}),
)

"""
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import Site
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.http import urlquote

#from photologue.models import Gallery

class MediaRSSFeed(Rss201rev2Feed):
    """Basic implementation of Yahoo Media RSS (mrss)
    http://video.search.yahoo.com/mrss

    Includes these elements in the Item feed:
    media:content
        url, width, height
    media:thumbnail
        url, width, height
    media:description
    media:title
    media:keywords
    """
    def rss_attributes(self):
        attrs = super(MediaRSSFeed, self).rss_attributes()
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        attrs['xmlns:atom'] = 'http://www.w3.org/2005/Atom'
        return attrs

    def add_item_elements(self, handler, item):
        """Callback to add elements to each item (item/entry) element."""
        super(MediaRSSFeed, self).add_item_elements(handler, item)

        if 'media' not in item:
            return True

        items = (item['media'],) if isinstance(item['media'], dict) else item['media']

        if len(items) > 1:
            handler.startElement(u"media:group", {})

        for item in items:

            if 'media:title' in item:
                handler.addQuickElement(u"media:title", item['title'])
            if 'media:description' in item:
                handler.addQuickElement(u"media:description", item['description'])

            if 'content_url' in item:
                content = {}
                for attr in ['url','width','height','medium','type','isDefault']:
                    if 'content_%s' % attr in item:
                        content[attr] = str(item['content_%s' % attr])
                handler.addQuickElement(u"media:content", '', content)

            if 'thumbnail_url' in item:
                thumbnail = {}
                for attr in ['url','width','height','time']:
                    if 'thumbnail_%s' % attr in item:
                        thumbnail[attr] = str(item['thumbnail_%s' % attr])
                handler.addQuickElement(u"media:thumbnail", '', thumbnail)

            if 'keywords' in item:
                handler.addQuickElement(u"media:keywords", item['keywords'])

        if len(items) > 1:
            handler.endElement(u"media:group")

class PhotologueFeed(Feed):
    """Basic Feed implementation for generating a MediaRSS feed for photologue galleries
    To customize, subclass and override these attributes:
        title
        description
        title_template
        description_template
        item_limit
    """
    feed_type = MediaRSSFeed

    sitename = Site.objects.get_current().name

    title = '%s Gallery' % (sitename,)
    description = '%s Photo Gallery' % (sitename,)
    title_template = 'gallery_feed_title.html'
    description_template = 'gallery_feed_description.html'
    item_limit = 10

    def get_object(self, bits):
        """
        Returns objects based on slug fed through URL
        e.g.
        <url-slug>/gallery-title-slug/
        returns photos in gallery-title-slug

        <url-slug>/
        returns latest 10 galleries with sample photos.
            links are to gallery feeds
        """

        if len(bits) == 0:
            return None
        elif len(bits) > 1:
            return ObjectDoesNotExist
        else:
            return Gallery.objects.get(title_slug__exact=bits[0])

    def link(self, gallery):
        """Returns link to either the archive list URL or specific gallery URL"""
        if gallery is None:
            return reverse('pl-gallery-archive')
        else:
            return gallery.get_absolute_url()

    def items(self, gallery):
        """Returns up to 'item_limit' public Gallery items or 'item_limit' public photos in a specified Gallery (default=10)
        """
        if gallery is None:
            return Gallery.objects.filter(is_public=True)[:self.item_limit]
        else:
            return gallery.public()[:self.item_limit]

    def item_pubdate(self, obj):
        return obj.date_added

    def item_extra_kwargs(self, obj):
        """Return a dictionary to the feedgenerator for each item to be added to the feed.
        If the object is a Gallery, uses a random sample image for use as the feed Item
        """
        if isinstance(obj, Gallery):
            photo = obj.sample(1)[0]
            photo.caption = obj.description
        else:
            photo = obj

        item = {'media:title': photo.title,
                'media:description': photo.caption,
                'content_url': photo.get_display_url(),
                'content_width': photo.get_display_size()[0],
                'content_height': photo.get_display_size()[1],
                'thumbnail_url': photo.get_thumbnail_url(),
                'thumbnail_width': photo.get_thumbnail_size()[0],
                'thumbnail_height': photo.get_thumbnail_size()[1],
               }

        if len(photo.tags) > 0:
           keywords = ','.join(photo.tags.split())
           item['keywords'] = keywords

        return item

# Convenience for supplying feed_dict to django.contrib.syndication.views.feed in url
photofeeds = {
    'gallery': PhotologueFeed,
}
