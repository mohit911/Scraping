from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.


class ScrapeUrl(models.Model):
    scrapeUrl_link = models.TextField(
        blank=False,
        null=False,
        unique=True,
        verbose_name='Website Url')

    scrape_time = models.IntegerField(
        blank=False,
        null=False,
        default='',
        verbose_name='Time Taken to scrape')

    head_data = models.TextField(
        blank=True,
        null=True,
        default='',
        verbose_name='Head Tag Data')

    created = models.DateTimeField(
        default=timezone.now)

    def __str__(self):
        """Unicode Method to Display Relevent data in Admin template."""
        return str(self.scrapeUrl_link)

    class Meta:
        """Information About the class."""

        verbose_name = "ScrapeUrl"
        verbose_name_plural = "ScrapeUrl's"


class ScrapeData(models.Model):
    scrapeUrl_link = models.ForeignKey(
        ScrapeUrl,
        default='',
        blank=False,
        null=False)

    image_link = models.TextField(
        blank=False,
        null=False,
        verbose_name='Image Url')

    image_width = models.DecimalField(
        max_digits=1000,
        decimal_places=2,
        default=0.00,
        verbose_name='Image Width')

    image_height = models.DecimalField(
        max_digits=1000,
        decimal_places=2,
        default=0.00,
        verbose_name='Image Height')

    created = models.DateTimeField(
        default=timezone.now)

    def __str__(self):
        """Unicode Method to Display Relevent data in Admin template."""
        return str(self.scrapeUrl_link)

    class Meta:
        """Information About the class."""

        verbose_name = "ScrapeData"
        verbose_name_plural = "ScrapeData"
