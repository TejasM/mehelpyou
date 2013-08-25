# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'UserProfile.recommandations_recieved'
        db.delete_column(u'userprofile_userprofile', 'recommandations_recieved')

        # Adding field 'UserProfile.recommendations_received'
        db.add_column(u'userprofile_userprofile', 'recommendations_received',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'UserProfile.recommandations_recieved'
        db.add_column(u'userprofile_userprofile', 'recommandations_recieved',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Deleting field 'UserProfile.recommendations_received'
        db.delete_column(u'userprofile_userprofile', 'recommendations_received')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'userprofile.userpic': {
            'Meta': {'object_name': 'UserPic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "'None'", 'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_info'", 'to': u"orm['auth.User']"})
        },
        u'userprofile.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'educations': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'groups': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'interests': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'lifetime_earning': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'money_current': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'num_connections': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_recommenders': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'paypal_email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75'}),
            'rating': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'recommendations_received': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'}),
            'skills': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['userprofile']