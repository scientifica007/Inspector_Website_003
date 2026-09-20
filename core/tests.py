from datetime import date
from django.test import TestCase,Client
from django.contrib.auth.models import User
from .models import *
class VisitSafetyTests(TestCase):
 def setUp(self):
  self.user=User.objects.create_user('inspector','', 'pw'); self.other=User.objects.create_user('other','', 'pw'); self.ins=Institution.objects.create(name='مؤسسة'); self.ref=Reference.objects.create(name='مرجع',shared=True); self.node=ReferenceNode.objects.create(reference=self.ref,stable_id='i1',title='بند',node_type='ITEM'); self.c=Client(); self.c.login(username='inspector',password='pw')
 def test_snapshot_survives_reference_change(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_name=self.ref.name,reference_snapshot={'name':self.ref.name,'nodes':[{'stable_id':'i1','title':'بند'}]}); self.node.title='تغيير'; self.node.save(); self.ref.delete(); v.refresh_from_db(); self.assertEqual(v.reference_snapshot['nodes'][0]['title'],'بند')
 def test_private_visibility(self):
  private=Reference.objects.create(name='خاص',owner=self.user); self.assertNotIn(private,Reference.objects.filter(shared=True,owner=self.other))
 def test_completed_cannot_be_deleted_by_owner(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),status='COMPLETED'); self.assertTrue(Visit.objects.filter(pk=v.pk).exists())
 def test_other_inspector_denied(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.other,date=date.today()); self.assertEqual(self.c.get('/visits/%s/'%v.pk).status_code,404)
 def test_export_has_version(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_snapshot={'name':'x'}); response=self.c.get('/visits/%s/export/'%v.pk); self.assertEqual(response.json()['schema_version'],'1.0')
