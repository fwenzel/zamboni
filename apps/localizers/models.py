from django.db import models

import amo.models
from translations.fields import TranslatedField


class L10nEventlog(amo.models.ModelBase):
    locale = models.CharField(max_length=30, default='')
    type = models.CharField(max_length=20, default='')
    action = models.CharField(max_length=40, default='')
    field = models.CharField(max_length=20, default='', null=True)
    user = models.ForeignKey('users.UserProfile')
    changed_id = models.PositiveIntegerField(
        default=0, help_text='id of the object being affected by the change')
    added = models.CharField(max_length=255, default='', null=True)
    removed = models.CharField(max_length=255, default='', null=True)
    notes = models.TextField()

    modified = None # no "modified" field

    class Meta:
        db_table = 'l10n_eventlog'


class L10nSettings(amo.models.ModelBase):
    """Per-locale L10n Dashboard settings"""
    locale = models.CharField(max_length=30, default='', unique=True)
    motd = TranslatedField()
    team_homepage = models.CharField(max_length=255, default='', null=True)

    class Meta:
        db_table = 'l10n_settings'
