from django.db import transaction
from django.utils import timezone
from .models import *
class ProposalError(Exception): pass
@transaction.atomic
def submit_reference(reference,user):
 if reference.owner_id!=user.id or reference.shared: raise ProposalError('لا يمكن إرسال هذا المرجع')
 snapshot={'name':reference.name,'nodes':list(reference.nodes.values('stable_id','title','node_type','parent_id','position'))}
 return ReferenceProposal.objects.create(reference=reference,submitter=user,snapshot=snapshot)
@transaction.atomic
def review_proposal(proposal,admin_user,approve):
 if not admin_user.is_staff or proposal.status!='PENDING': raise ProposalError('مراجعة غير صالحة')
 proposal.status='APPROVED' if approve else 'REJECTED'; proposal.reviewed_by=admin_user; proposal.reviewed_at=timezone.now(); proposal.save()
 if approve:
  shared=Reference.objects.create(name=proposal.snapshot['name'],shared=True,snapshot=proposal.snapshot)
  for n in proposal.snapshot['nodes']:
   parent=None
   if n['parent_id']: parent=ReferenceNode.objects.filter(pk=n['parent_id'],reference=proposal.reference).first()
   ReferenceNode.objects.create(reference=shared,stable_id=n['stable_id'],title=n['title'],node_type=n['node_type'],parent=parent,position=n['position'])
  return shared
