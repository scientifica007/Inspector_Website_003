import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from .models import *
from .services import apply_guide, AssignmentError
@login_required
def dashboard(request): return render(request,'dashboard.html',{'visits':Visit.objects.filter(inspector=request.user).select_related('institution'),'institutions':Institution.objects.filter(active=True),'references':Reference.objects.filter(shared=True)|Reference.objects.filter(owner=request.user)})
@login_required
def institutions(request):
 if request.method=='POST': Institution.objects.create(name=request.POST['name'],kind=request.POST.get('kind','')); return redirect('institutions')
 return render(request,'institutions.html',{'institutions':Institution.objects.all()})
@login_required
def references(request):
 if request.method=='POST':
  Reference.objects.create(name=request.POST['name'],owner=request.user,shared=False); messages.success(request,'تم إنشاء المرجع الخاص'); return redirect('references')
 return render(request,'references.html',{'references':Reference.objects.filter(shared=True)|Reference.objects.filter(owner=request.user)})
@login_required
@transaction.atomic
def visit_new(request):
 if request.method=='POST':
  ins=get_object_or_404(Institution,pk=request.POST['institution']); ref=Reference.objects.filter(pk=request.POST.get('reference')).first(); snap={'id':ref.pk,'name':ref.name,'nodes':list(ref.nodes.values('stable_id','title','node_type','parent_id','position'))} if ref else {'id':None,'name':'بدون مرجع','nodes':[]}; v=Visit.objects.create(institution=ins,inspector=request.user,date=request.POST['date'],reference_name=snap['name'],reference_snapshot=snap)
  return redirect('visit_detail',v.pk)
 return render(request,'visit_new.html',{'institutions':Institution.objects.filter(active=True),'references':Reference.objects.filter(shared=True)|Reference.objects.filter(owner=request.user)})
@login_required
def apply_guide_view(request,pk,guide_id):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user)
 guide=get_object_or_404(Guide,pk=guide_id,active=True)
 if request.method=='POST':
  apply_guide(v,guide); messages.success(request,'تم تطبيق الدليل على نطاق الزيارة');
 return redirect('visit_detail',pk)
@login_required
def add_scope_node(request,pk):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user)
 if request.method=='POST' and v.status=='DRAFT':
  stable=request.POST.get('stable_id'); raw=next((x for x in v.reference_snapshot.get('nodes',[]) if x.get('stable_id')==stable),None)
  if raw and not v.items.filter(stable_id=stable).exists(): VisitNode.objects.create(visit=v,stable_id=stable,title=raw.get('title',''),node_type=raw.get('node_type','ITEM'),origin='MANUAL',parent_id_snapshot=str(raw.get('parent_id') or ''))
 return redirect('visit_detail',pk)
@login_required
def toggle_exclusion(request,pk,item_id):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user); item=get_object_or_404(VisitNode,pk=item_id,visit=v)
 if request.method=='POST' and v.status=='DRAFT' and not item.scope_locked: item.excluded=not item.excluded; item.save(update_fields=['excluded'])
 return redirect('visit_detail',pk)
@login_required
def visit_detail(request,pk):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user)
 if request.method=='POST' and v.status=='DRAFT':
  for item in v.items.all(): item.result=request.POST.get('result_'+str(item.pk),item.result); item.observation=request.POST.get('obs_'+str(item.pk),item.observation); item.save()
  if request.POST.get('add'):
   title=request.POST.get('title','عنصر محلي'); VisitNode.objects.create(visit=v,stable_id='local-'+str(v.items.count()+1),title=title,node_type='ITEM',origin='LOCAL')
  messages.success(request,'تم حفظ الزيارة')
 nodes=v.items.all(); progress=(nodes.filter(result__in=['CONFORM','NONCONFORM','NA'],excluded=False).count(),nodes.filter(excluded=False).count())
 selected=set(nodes.values_list('stable_id',flat=True)); available=[x for x in v.reference_snapshot.get('nodes',[]) if x.get('stable_id') not in selected]
 return render(request,'visit_detail.html',{'visit':v,'items':nodes,'progress':progress,'available':available,'guides':Guide.objects.filter(active=True,reference__name=v.reference_name)})
@login_required
def complete(request,pk):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user)
 if request.method=='POST' and v.status=='DRAFT' and not v.items.filter(excluded=False,completion_required=True).exclude(result__in=['CONFORM','NONCONFORM','NA']).exists(): v.status='COMPLETED'; v.save()
 else: messages.error(request,'لا يمكن إكمال الزيارة بهذه الحالة')
 return redirect('visit_detail',pk)
@login_required
def delete_visit(request,pk):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user)
 if request.method=='POST' and v.status=='DRAFT': v.delete(); return redirect('dashboard')
 messages.error(request,'لا يمكن حذف زيارة مكتملة'); return redirect('visit_detail',pk)
@login_required
def export_visit(request,pk):
 v=get_object_or_404(Visit,pk=pk,inspector=request.user); data={'schema_version':'1.0','visit_id':v.pk,'institution':v.institution.name,'inspector':v.inspector.username,'date':v.date.isoformat(),'status':v.status,'reference':v.reference_snapshot,'scope':[{'id':n.stable_id,'title':n.title,'selected':n.selected,'excluded':n.excluded,'origin':n.origin,'result':n.result,'observation':n.observation,'completion_required':n.completion_required,'scope_locked':n.scope_locked} for n in v.items.all()]}; return JsonResponse(data,json_dumps_params={'ensure_ascii':False,'indent':2})
