import slugify
from cgi import escape
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.args.get('next_url'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def slug(value):
    return slugify.slugify(value)

def html_params(**kwargs):
    """
    Generate HTML parameters from inputted keyword arguments.

    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters.  Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.

    >>> html_params(name='text1', id='f', class_='text')
    u'class="text" id="f" name="text1"'
    """
    params = []
    for k,v in sorted(kwargs.iteritems()):
        if k in ('class_', 'class__', 'for_'):
            k = k[:-1]
        if v is True:
            params.append(k)
        else:
            params.append(u'%s="%s"' % (unicode(k), escape(unicode(v), quote=True)))
    return u' '.join(params)
