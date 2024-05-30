# -*- coding: UTF-8 -*-
from django.contrib.sitemaps import Sitemap

from .mixins.sitemap import SitemapMixin
from .models.mineral import Mineral

STATIC_PAGES_MAP = {
    "index": {"location": "/", "changefreq": "weekly"},
    "explore": {"location": "/explore", "changefreq": "weekly"},
    "blog": {"location": "/blog", "changefreq": "weekly"},
    "about": {"location": "/about", "changefreq": "monthly"},
    "contact": {"location": "/contact", "changefreq": "monthly"},
    "privacy": {"location": "/privacy-policy", "changefreq": "monthly"},
    "terms": {"location": "/terms-of-service", "changefreq": "monthly"},
}


class PageSitemap(SitemapMixin, Sitemap):

    def items(self):
        return [key for key, value in STATIC_PAGES_MAP.items()]

    def location(self, obj):
        return STATIC_PAGES_MAP[obj]["location"]

    def changefreq(self, obj):
        return STATIC_PAGES_MAP[obj]["changefreq"]


class MineralSitemap(SitemapMixin, Sitemap):

    changefreq = "daily"
    priority = 0.5
    limit = 3000

    def items(self):
        return Mineral.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return "/explore/" + obj.slug + "/"
