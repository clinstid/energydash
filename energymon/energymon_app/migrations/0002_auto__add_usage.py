# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Usage'
        db.create_table(u'energymon_app_usage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('time_of_reading', self.gf('django.db.models.fields.DateTimeField')()),
            ('watts', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'energymon_app', ['Usage'])


    def backwards(self, orm):
        # Deleting model 'Usage'
        db.delete_table(u'energymon_app_usage')


    models = {
        u'energymon_app.usage': {
            'Meta': {'object_name': 'Usage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_of_reading': ('django.db.models.fields.DateTimeField', [], {}),
            'watts': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['energymon_app']