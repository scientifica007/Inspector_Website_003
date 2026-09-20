from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import *
class Command(BaseCommand):
 help='Create safe repeatable demo data'
 def handle(self,*args,**opts):
  admin,_=User.objects.get_or_create(username='admin',defaults={'is_staff':True,'is_superuser':True}); admin.set_password('Admin123!'); admin.save()
  inspector,_=User.objects.get_or_create(username='inspector'); inspector.set_password('Inspector123!'); inspector.save()
  for name,kind in [('مركز وهران المهني','تكوين مهني'),('معهد التقنية','معهد')]: Institution.objects.get_or_create(name=name,defaults={'kind':kind})
  ref,_=Reference.objects.get_or_create(name='مرجع التفتيش البيداغوجي',shared=True,defaults={'snapshot':{}})
  if not ref.nodes.exists():
   branch=ReferenceNode.objects.create(reference=ref,stable_id='b-education',title='التنظيم البيداغوجي',node_type='BRANCH')
   spec=ReferenceNode.objects.create(reference=ref,stable_id='s-attendance',title='متابعة الدخول التكويني',node_type='SPEC',parent=branch)
   for sid,title in [('i-register','سجل الحضور محدث'),('i-schedule','البرنامج الأسبوعي معلن')]: ReferenceNode.objects.create(reference=ref,stable_id=sid,title=title,node_type='ITEM',parent=spec)
  self.stdout.write(self.style.SUCCESS('Demo data ready: admin/Admin123!, inspector/Inspector123!'))
