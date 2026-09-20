from django.db import transaction
from django.utils import timezone
from .models import *
class AssignmentError(Exception): pass
@transaction.atomic
def issue_assignment(assignment, entries):
 if assignment.status!='DRAFT' or assignment.visit.status!='DRAFT': raise AssignmentError('لا يمكن إصدار التكليف')
 ids={x['stable_id'] for x in entries}; available={x.stable_id for x in assignment.visit.items.all()}
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
 assignment.status='REVOKED'; assignment.reason=reason; assignment.revoked_at=timezone.now(); assignment.save(update_fields=['status','reason','revoked_at'])
 for item in assignment.visit.items.all():
  other=AssignmentEntry.objects.filter(assignment__visit=assignment.visit,stable_id=item.stable_id,assignment__status='ISSUED').exclude(assignment=assignment)
  item.scope_locked=other.filter(scope_locked=True).exists(); item.completion_required=other.filter(completion_required=True).exists(); item.save(update_fields=['scope_locked','completion_required'])
 return assignment
