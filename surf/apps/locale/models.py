from django.db import models

from surf.apps.core.models import UUIDModel


class Locale(UUIDModel):

    asset = models.CharField('Asset ID', max_length=512, unique=True)
    en = models.CharField('English, en', max_length=5120, null=True, blank=True)
    nl = models.CharField('Dutch, nl', max_length=5120, null=False, blank=False)
    is_fuzzy = models.BooleanField(default=False)

    @property
    def translation_key(self):
        return f"{self.asset}"

    def __str__(self):
        return self.asset

    class Meta:
        verbose_name = "Localization"
        verbose_name_plural = "Localizations"


class LocaleHTML(UUIDModel):

    asset = models.CharField('Asset ID', max_length=512, unique=True)
    en = models.TextField('English, en', max_length=16384, null=True, blank=True)
    nl = models.TextField('Dutch, nl', max_length=16384, null=False, blank=False)
    is_fuzzy = models.BooleanField(default=False)

    @property
    def translation_key(self):
        return f"html-{self.asset}"

    def __str__(self):
        return self.asset

    class Meta:
        verbose_name = "Localization with HTML"
        verbose_name_plural = "Localizations with HTML"
