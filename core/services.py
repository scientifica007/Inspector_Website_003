from django.db import transaction
from django.utils import timezone
from .models import *
class AssignmentError(Exception): pass

def apply_guide(visit, guide):
 if visit.status!='DRAFT': return visit
 if guide.reference_id != visit.reference_snapshot.get('id'):
  return visit
 # compatibility is based on frozen stable identifiers, never live reference content
 allowed={x.get('stable_id') for x in visit.reference_snapshot.get('nodes',[])}
 wanted=set(guide.node_ids) & allowed
 existing=set(visit.items.values_list('stable_id',flat=True))
 for node in guide.reference.nodes.filter(stable_id__in=wanted):
  if node.stable_id not in existing:
   VisitNode.objects.create(visit=visit,stable_id=node.stable_id,title=node.title,node_type=node.node_type,origin='GUIDE',parent_id_snapshot=node.parent.stable_id if node.parent else '')
 return visit
@transaction.atomic
def issue_assignment(assignment, entries):
 if assignment.status!='DRAFT' or assignment.visit.status!='DRAFT': raise AssignmentError('لا يمكن إصدار التكليف')
 ids={x['stable_id'] for x in entries}; available={x.stable_id for x in assignment.visit.items.all()}
 if not ids: raise AssignmentError('يجب أن يحتوي التكليف على عنصر واحد على الأقل')
 if not ids.issubset(available): raise AssignmentError('يوجد عنصر غير موجود في snapshot')
 assignment.entries.all().delete()
 for x in entries: assignment.entries.create(**x)
 assignment.status='ISSUED'; assignment.issued_at=timezone.now(); assignment.save(update_fields=['status','issued_at'])
 for entry in assignment.entries.select_related('assignment'):
  item=assignment.visit.items.get(stable_id=entry.stable_id)
  item.scope_locked |= entry.scope_locked; item.completion_required |= entry.completion_required; item.save(update_fields=['scope_locked','completion_required'])
 return assignment
@transaction.atomic
def revoke_assignment(assignment,reason):
 if assignment.status!='ISSUED' or assignment.visit.status!='DRAFT': raise AssignmentError('لا يمكن الإلغاء')
 if not reason or not reason.strip(): raise AssignmentError('سبب الإلغاء مطلوب')
 assignment.status='REVOKED'; assignment.reason=reason; assignment.revoked_at=timezone.now(); assignment.save(update_fields=['status','reason','revoked_at'])
 for item in assignment.visit.items.all():
  other=AssignmentEntry.objects.filter(assignment__visit=assignment.visit,stable_id=item.stable_id,assignment__status='ISSUED').exclude(assignment=assignment)
  item.scope_locked=other.filter(scope_locked=True).exists(); item.completion_required=other.filter(completion_required=True).exists(); item.save(update_fields=['scope_locked','completion_required'])
 return assignment
