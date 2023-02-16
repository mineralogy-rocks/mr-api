# -*- coding: UTF-8 -*-
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator, slugify


def formula_to_html(formula):
    if formula:
        replacements = [
            dict(to_replace=r"(_)(.*?_)", replacement=r"\1<sub>\2</sub>"),
            dict(to_replace=r"(\^)(.*?\^)", replacement=r"\1<sup>\2</sup>"),
            dict(to_replace=r"_", replacement=""),
            dict(to_replace=r"\^", replacement=""),
        ]
        parsed = formula
        [
            parsed := re.sub(replacement["to_replace"], replacement["replacement"], parsed)
            for replacement in replacements
        ]
        return mark_safe(parsed)
    return None


def get_relation_note(relation_type):
    note = ""
    if relation_type == 1:
        note = "Synonym"
    elif relation_type == 2:
        note = "Mixture"
    elif relation_type == 3:
        note = "Mixture (?)"
    elif relation_type == 4:
        note = "Minerals structurally related to group"
    elif relation_type == 5:
        note = "Associated Minerals at the locality"
    elif relation_type == 6:
        note = "Epitaxial Relationships"
    elif relation_type == 7:
        note = "Polymorph of"
    elif relation_type == 8:
        note = "Isostructural with"
    elif relation_type == 9:
        note = "Minerals chemically related to group"
    elif relation_type == 10:
        note = "Common Associates"
    elif relation_type == 11:
        note = "Mineralogy of  Essential minerals - these are minerals that are required within the classification of this rock"
    elif relation_type == 12:
        note = "Ores of  Common ore minerals of"
    elif relation_type == 13:
        note = "Mineralogy of  Accessory minerals - these are minor components, often far less than 1 percent of the total mineral material"
    return note


def send_email(subject, template, recepients, context=None):
    html_content = render_to_string(template, context)
    email_message = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, email_message, settings.DEFAULT_FROM_EMAIL, recepients)
    msg.attach_alternative(html_content, "text/html")

    msg.send()


def shorten_text(text, limit=100, strip_html=False, html=False):
    text = text.strip()
    if strip_html:
        text = strip_tags(text)
    return Truncator(text).chars(limit, truncate="...", html=html)


def unique_slugify(instance, value, slug_field_name='slug', queryset=None, delimiter='-'):
    """
    From snippet https://djangosnippets.org/snippets/690/

    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, delimiter)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-1' to the end and try again
    # (then '-2', etc).
    next = 1
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (delimiter, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, delimiter)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)
    return instance


def _slug_strip(value, delimiter='-'):
    """
    From snippet https://djangosnippets.org/snippets/690/

    Cleans up a slug by removing slug delimiter characters that occur at the
    beginning or end of a slug.

    If an alternate delimiter is used, it will also replace any instances of
    the default '-' delimiter with the new delimiter.
    """
    delimiter = delimiter or ''
    if delimiter == '-' or not delimiter:
        re_del = '-'
    else:
        re_del = '(?:-|%s)' % re.escape(delimiter)
    # Remove multiple instances and if an alternate delimiter is provided,
    # replace the default '-' delimiter.
    if delimiter != re_del:
        value = re.sub('%s+' % re_del, delimiter, value)
    # Remove delimiter from the beginning and end of the slug.
    if delimiter:
        if delimiter != '-':
            re_del = re.escape(delimiter)
        value = re.sub(r'^%s+|%s+$' % (re_del, re_del), '', value)
    return value
