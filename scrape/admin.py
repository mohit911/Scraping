from django.contrib import admin
from scrape.models import ScrapeData, ScrapeUrl
# Register your models here.

admin.site.register(ScrapeUrl)
admin.site.register(ScrapeData)
