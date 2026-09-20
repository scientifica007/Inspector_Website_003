from datetime import date
from django.test import TestCase,Client
from django.contrib.auth.models import User
from .models import *
from .services import issue_assignment, revoke_assignment, apply_guide, AssignmentError
class VisitSafetyTests(TestCase):
 def setUp(self):
  self.user=User.objects.create_user('inspector','', 'pw'); self.other=User.objects.create_user('other','', 'pw'); self.ins=Institution.objects.create(name='مؤسسة'); self.ref=Reference.objects.create(name='مرجع',shared=True); self.node=ReferenceNode.objects.create(reference=self.ref,stable_id='i1',title='بند',node_type='ITEM'); self.c=Client(); self.c.login(username='inspector',password='pw')
 def test_snapshot_survives_reference_change(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_name=self.ref.name,reference_snapshot={'name':self.ref.name,'nodes':[{'stable_id':'i1','title':'بند'}]}); self.node.title='تغيير'; self.node.save(); self.ref.delete(); v.refresh_from_db(); self.assertEqual(v.reference_snapshot['nodes'][0]['title'],'بند')
 def test_private_visibility(self):
  private=Reference.objects.create(name='خاص',owner=self.user); self.assertNotIn(private,Reference.objects.filter(shared=True,owner=self.other))
 def test_private_reference_creation_is_owned(self):
  response=self.c.post('/references/',{'name':'مرجعي'}); self.assertEqual(response.status_code,302); self.assertTrue(Reference.objects.filter(name='مرجعي',owner=self.user,shared=False).exists())
 def test_completed_cannot_be_deleted_by_owner(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),status='COMPLETED'); self.assertTrue(Visit.objects.filter(pk=v.pk).exists()); self.assertEqual(self.c.post('/visits/%s/delete/'%v.pk).status_code,302); self.assertTrue(Visit.objects.filter(pk=v.pk).exists())
 def test_draft_can_be_deleted_by_owner(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today()); self.assertEqual(self.c.post('/visits/%s/delete/'%v.pk).status_code,302); self.assertFalse(Visit.objects.filter(pk=v.pk).exists())
 def test_completed_visit_is_immutable_in_view(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),status='COMPLETED'); VisitNode.objects.create(visit=v,stable_id='i1',title='قديم',node_type='ITEM',result='CONFORM'); self.c.post('/visits/%s/'%v.pk,{'result_1':'NONCONFORM','obs_1':'تعديل'}); self.assertEqual(v.items.first().result,'CONFORM')
 def test_required_item_blocks_completion(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today()); VisitNode.objects.create(visit=v,stable_id='i1',title='إلزامي',node_type='ITEM',completion_required=True); self.c.post('/visits/%s/complete/'%v.pk); v.refresh_from_db(); self.assertEqual(v.status,'DRAFT')
 def test_other_inspector_denied(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.other,date=date.today()); self.assertEqual(self.c.get('/visits/%s/'%v.pk).status_code,404)
 def test_export_has_version(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_snapshot={'name':'x'}); response=self.c.get('/visits/%s/export/'%v.pk); self.assertEqual(response.json()['schema_version'],'1.0')
 def test_assignment_issue_is_atomic_and_adds_constraints(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today()); item=VisitNode.objects.create(visit=v,stable_id='i1',title='بند',node_type='ITEM'); a=Assignment.objects.create(visit=v,title='تكليف')
  issue_assignment(a,[{'stable_id':'i1','scope_locked':True,'completion_required':True}]); item.refresh_from_db(); self.assertTrue(item.scope_locked and item.completion_required)
  bad=Assignment.objects.create(visit=v,title='فاسد')
  with self.assertRaises(AssignmentError): issue_assignment(bad,[{'stable_id':'missing'}])
  self.assertEqual(bad.entries.count(),0); self.assertEqual(bad.status,'DRAFT')
 def test_guide_is_idempotent_and_snapshot_bounded(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_snapshot={'id':self.ref.pk,'nodes':[{'stable_id':'i1'}]}); guide=Guide.objects.create(name='دليل',reference=self.ref,node_ids=['i1','new'])
  apply_guide(v,guide); apply_guide(v,guide); self.assertEqual(v.items.count(),1); self.assertEqual(v.items.first().origin,'GUIDE')
 def test_guide_from_other_reference_is_ignored(self):
  other=Reference.objects.create(name='آخر',shared=True); Guide.objects.create(name='غير متوافق',reference=other,node_ids=['i1']); v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),reference_snapshot={'id':self.ref.pk,'nodes':[{'stable_id':'i1'}]}); guide=Guide.objects.get(name='غير متوافق'); apply_guide(v,guide); self.assertEqual(v.items.count(),0)
 def test_revoke_is_blocked_after_completion(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today(),status='COMPLETED'); VisitNode.objects.create(visit=v,stable_id='i1',title='بند',node_type='ITEM'); a=Assignment.objects.create(visit=v,title='A');
  with self.assertRaises(AssignmentError): revoke_assignment(a,'متأخر')
 def test_overlapping_revoke_keeps_other_obligation(self):
  v=Visit.objects.create(institution=self.ins,inspector=self.user,date=date.today()); VisitNode.objects.create(visit=v,stable_id='i1',title='بند',node_type='ITEM'); a=Assignment.objects.create(visit=v,title='A'); b=Assignment.objects.create(visit=v,title='B'); issue_assignment(a,[{'stable_id':'i1','scope_locked':True}]); issue_assignment(b,[{'stable_id':'i1','completion_required':True}]); revoke_assignment(a,'انتهى'); item=v.items.get(); self.assertFalse(item.scope_locked); self.assertTrue(item.completion_required)
