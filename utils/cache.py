'''
Cache invalidation function from here http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django
'''
def expire_view_cache(view_name, args=[], namespace=None, key_prefix=None):
    """
    This function allows you to invalidate any view-level cache.
        view_name: view function you wish to invalidate or it's named url pattern
        args: any arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)
    """
    from django.core.urlresolvers import reverse
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key
    from django.core.cache import cache
    # create a fake request object
    request = HttpRequest()
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    request.path = reverse(view_name, args=args)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            # Delete the cache entry.
            #
            # Note that there is a possible race condition here, as another
            # process / thread may have refreshed the cache between
            # the call to cache.get() above, and the cache.set(key, None)
            # below.  This may lead to unexpected performance problems under
            # severe load.
            cache.set(key, None, 0)
        return True
    return False