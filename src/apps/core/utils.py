# -*- coding: UTF-8 -*-
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.text import slugify


def process_text(notes):
    from collections import Counter

    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    nltk.download("stopwords")
    nltk.download("punkt")

    # colors is a list of all primary colors
    colors = [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "indigo",
        "violet",
        "purple",
        "pink",
        "brown",
        "black",
        "white",
        "gray",
        "grey",
        "beige",
        "cream",
        "teal",
        "turquoise",
        "gold",
        "silver",
        "bronze",
        "copper",
        "brass",
        "platinum",
        "ruby",
        "sapphire",
        "emerald",
        "diamond",
        "pearl",
        "amber",
        "amethyst",
        "aquamarine",
        "citrine",
        "coral",
        "garnet",
        "jade",
        "onyx",
        "opal",
        "peridot",
        "quartz",
        "topaz",
        "turquoise",
        "zircon",
        "azure",
        "cerulean",
        "cobalt",
        "cyan",
        "indigo",
        "lapis",
        "lazuli",
        "sapphire",
        "ultramarine",
        "vermilion",
        "viridian",
        "alabaster",
        "ash",
        "bone",
        "charcoal",
        "cloud",
        "ebony",
        "fog",
        "frost",
        "ivory",
        "lead",
        "milk",
        "oyster",
        "powder",
        "smoke",
        "snow",
        "steel",
        "stone",
        "storm",
        "thunder",
        "vanilla",
        "ashen",
        "ashy",
        "blanched",
        "bleached",
        "blond",
        "blonde",
        "bronzed",
        "brunette",
        "burnt",
        "caramel",
        "chestnut",
        "chocolate",
        "cocoa",
        "coffee",
        "coppery",
        "dark",
        "ebony",
        "fair",
        "fawn",
        "flaxen",
        "golden",
        "gray",
        "grey",
        "honey",
        "light",
        "mahogany",
        "nut-brown",
        "olive",
        "pale",
        "peach",
        "porcelain",
        "red",
        "rosy",
        "ruddy",
        "russet",
        "sallow",
        "sandy",
        "sepia",
        "silver",
        "skin",
    ]
    _colors_regex = re.compile(r"%s" % "(" + ")|(".join([color + "" for color in colors]) + ").*", re.IGNORECASE)
    notes = "Black; Black, dark brown; Black, dark green; Black, dark-green, greenish-brown, yellow; Black, dark-violet, light sky-blue.; Black-green, dark green; Black; mustard yellow to brownish yellow; Black or dark blue-green; Blue-grey; Bluish black; Bluish-black to black.; Bluish-black to black, purple; Bluish green; Bluish-green to green.; Bluish grey; Bright green to emerald green; Brown; Brownish black; Brownish-black; Brownish yellow; Brown to brownish-red, rose-red, or yellow, grey-brown, and also pale to dark green. dark green blue and grey blue; Brown to brownish-red, rose-red, yellow, grey-brown, also pale to dark green.; Cherry red to very dark red; Clove-brown to dark brown, grey to white, green.; Clove-brown to dark brown, grey to white, pale green.; Cobalt-blue to violet-blue.; Cobalt-blue to violet-blue, lavender-gray, gray, colorless; Colourless to white; Crystals are pale bluish-grey; Dark bluish-green; Dark brown to black; Dark greenish; Dark greenish black; Dark green to black, greenish-brown, more rarely lighter green; Dark grey-blue to violet-blue; Dark-grey to greyish-black.; Dark mauve-red; Dark mauve-red (?); Dark red to brownish-lilac; Emerald green; Emerald green to pale green; Gray-white; Green; Green, black; Green, blue; Green-brown, black; Green, brownish, black; Green, green-black, grey-green, or black; Greenish black; Greenish-brown; Greenish-brown to dark green, black.; Greenish gray; Greenish grey; Green to brownish-green; Grey-green; Grey-green; blue-grey; Grey to lavender-blue.; Light blue to blue-black.; Light-brown, brown, greenish-brown to dark green and black.; Light greenish-blue; Light-greenish to colourless; Light green to light yellow, grey-black; Medium green to dark green to green-black to black, also brownish-green.; Medium green to dark green to green-black to black, brown; Medium green to dark green to green-black to black, brown (rare).; Nd; Pale brown; Pale greenish-grey to brown; Pale pink; Pale yellow, honey-yellow, yellow-brown to light brown, white (thin fibres); Pale-yellow to colourless; Pink-orange; Pink to red; Reddish-black to black.; Reddish brown; Red-orange; Sky-blue; grey; grey-violet; Straw yellow, pale orange; Straw yellow to brown colour; Translucent dark green, brown, grey, colourless; Usually black, also commonly light blue to blue-black, gray-blue, gray, brown; Very pale pinkish-brown; White, brown, colourless, grey, light green, green, light yellow, pink-violet; White, greenish grey, green, clove brown, or brownish green; White, grey, pale to dark green, also brown and pale pinkish-brown; White to brownish-yellow."
    stop_words = set(stopwords.words("english"))

    cleaned = []
    words = word_tokenize(notes.lower())
    for word in words:
        if word.isalnum() and word not in stop_words:
            if _colors_regex.match(word):
                _match_group = _colors_regex.match(word).group()
                if _match_group:
                    cleaned.append(_match_group)

    counts = Counter(cleaned)
    print(counts)

    return cleaned


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


def unique_slugify(instance, value, slug_field_name="slug", queryset=None, delimiter="-"):
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
        end = "%s%s" % (delimiter, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[: slug_len - len(end)]
            slug = _slug_strip(slug, delimiter)
        slug = "%s%s" % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)
    return instance


def _slug_strip(value, delimiter="-"):
    """
    From snippet https://djangosnippets.org/snippets/690/

    Cleans up a slug by removing slug delimiter characters that occur at the
    beginning or end of a slug.

    If an alternate delimiter is used, it will also replace any instances of
    the default '-' delimiter with the new delimiter.
    """
    delimiter = delimiter or ""
    if delimiter == "-" or not delimiter:
        re_del = "-"
    else:
        re_del = "(?:-|%s)" % re.escape(delimiter)
    # Remove multiple instances and if an alternate delimiter is provided,
    # replace the default '-' delimiter.
    if delimiter != re_del:
        value = re.sub("%s+" % re_del, delimiter, value)
    # Remove delimiter from the beginning and end of the slug.
    if delimiter:
        if delimiter != "-":
            re_del = re.escape(delimiter)
        value = re.sub(r"^%s+|%s+$" % (re_del, re_del), "", value)
    return value


def add_label(value, uncertainty=None, label: str = "") -> str:
    if value:
        _label = f"{value}"
        if uncertainty:
            _label += f"±{uncertainty}"
        return f"{_label}{label}"
    return None
