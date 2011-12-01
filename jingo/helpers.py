# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _
from django.template.defaulttags import CsrfTokenNode
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse

from django.conf import settings

import re
import jinja2

from jingo import register


@register.function
@jinja2.contextfunction
def csrf(context):
    return jinja2.Markup(CsrfTokenNode().render(context))


@register.filter
def f(string, *args, **kwargs):
    """
    Uses ``str.format`` for string interpolation.

    >>> {{ "{0} arguments and {x} arguments"|f('positional', x='keyword') }}
    "positional arguments and keyword arguments"
    """
    string = unicode(string)
    return string.format(*args, **kwargs)


@register.filter
def fe(string, *args, **kwargs):
    """Format a safe string with potentially unsafe arguments, then return a
    safe string."""

    string = unicode(string)

    args = [jinja2.escape(smart_unicode(v)) for v in args]

    for k in kwargs:
        kwargs[k] = jinja2.escape(smart_unicode(kwargs[k]))

    return jinja2.Markup(string.format(*args, **kwargs))


@register.filter
def nl2br(string):
    """Turn newlines into <br>."""
    if not string:
        return ''
    return jinja2.Markup('<br>'.join(jinja2.escape(string).splitlines()))


@register.filter
def datetime(t, fmt=None):
    """Call ``datetime.strftime`` with the given format string."""
    if fmt is None:
        fmt = _('%B %e, %Y')
    return smart_unicode(t.strftime(fmt.encode('utf-8'))) if t else u''


@register.filter
def ifeq(a, b, text):
    """Return ``text`` if ``a == b``."""
    return jinja2.Markup(text if a == b else '')


@register.filter
def class_selected(a, b):
    """Return ``'class="selected"'`` if ``a == b``."""
    return ifeq(a, b, 'class="selected"')


@register.filter
def field_attrs(field_inst, **kwargs):
    """Adds html attributes to django form fields"""
    field_inst.field.widget.attrs.update(kwargs)
    return field_inst


@register.function(override=False)
def url(viewname, *args, **kwargs):
    """Return URL using django's ``reverse()`` function."""
    return reverse(viewname, args=args, kwargs=kwargs)
    
    
@register.filter
def format_date(value, fmt="%d.%m.%Y %H:%M:%S"):
    '''
    Fileter for date formating

    @param value: date
    @param fmt: format
    @return: string
    '''

    from django.utils import translation, formats
    from django.utils.dateformat import format
    translation.activate(translation.get_language())

    if settings.USE_L10N and hasattr(settings, fmt):
        return formats.date_format(value, fmt)
    return format(value, fmt)
    

@register.test
def is_dict(value):
    return isinstance(value, dict)


@register.filter
def random_from_splited_string(value):
    import random

    list = value.split(',')
    value = list[random.randint(0, len(list) - 1)]
    return value.strip()


@register.filter
def hidereferer(value):
    from django.utils.http import urlquote
    return u'%s://%s/?%s' % (
        settings.HIDEREFERER_PROTOCOL,
        settings.HIDEREFERER_HOST,
        urlquote(value)
    )


@register.filter
def normalize_phone(value):
    value = unicode(value)
    value = value.strip()
    l = len(value)

    if l < 5:
        return value

    value = re.sub('[^+0-9]', '', value)

    l = len(value)
    if l == 7:
        value = '+7495' + value
    elif l == 10:
        value = '+7' + value
    elif l == 11 and value[0] == '7':
        value = '+' + value

    value = re.sub('^8', '+7', value)
    value = re.sub('^\+(7|380|375|1)([0-9]{2,3})([0-9]{3})([0-9]{2})([0-9]{2})',
                   '+\\1 (\\2) \\3-\\4-\\5',
                   value)
    return value


@register.filter
def normalize_car_num(value):
    return value


@register.filter
def quoted_printable(value):
    from email import Charset
    Charset.add_charset('utf-8', Charset.QP, Charset.QP, 'utf-8')
    return value.encode('utf-8').encode('quoted-printable')
