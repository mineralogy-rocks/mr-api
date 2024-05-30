# -*- coding: UTF-8 -*-
from django.conf import settings


class SitemapMixin(object):

    def _urls(self, page, protocol, domain):
        return super()._urls(page, protocol, settings.FRONTEND_DOMAIN)
