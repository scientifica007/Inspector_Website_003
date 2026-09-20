# Inspector_Website_003

منصة Django عربية RTL لإدارة التفتيش والزيارات مع حماية السجل التاريخي.

## التشغيل
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver 0.0.0.0:8000
```
اضبط `DJANGO_SECRET_KEY` و`DJANGO_ALLOWED_HOSTS` (قائمة مفصولة بفواصل) في بيئة الإنتاج. لا يوجد عنوان IP محلي ثابت.

## الاختبارات والفحص
```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py test
```

## قرارات المجال
- المرجع مستقل عن الزيارة؛ عند إنشاء الزيارة تُحفظ `reference_snapshot`، لذلك تعديل/حذف المرجع لا يغير التاريخ.
- نطاق الزيارة يبدأ فارغًا، والعناصر تحمل `selected` و`excluded` و`origin` (MANUAL/GUIDE/ASSIGNMENT/LOCAL/LEGACY). الاستبعاد ناعم ويحفظ النتيجة والملاحظة.
- Guide اقتراح اختياري، بينما Assignment كيان رسمي مستقل (DRAFT/ISSUED) مع قيود scope وcompletion؛ حقول النماذج موجودة لتوسعة خدمات الإصدار والإلغاء الذرية.
- الزيارة DRAFT قابلة للتحديث من صاحبها فقط، وCOMPLETED محمية منطقيًا؛ الإكمال يمنع وجود المتطلبات الإلزامية غير المنجزة.
- التصدير JSON versioned وحتمي البنية ويشمل snapshot والنطاق والنتائج والملاحظات والقيود.
- الصلاحيات خادمية عبر login وquery ownership، مع CSRF وORM.

## النطاق الحالي وHuman Acceptance
الواجهة الأساسية، المؤسسات، المراجع، snapshots، النطاق المحلي، التسجيل والنتائج والتصدير متاحة. إدارة Guides/Assignments المتقدمة (شاشات الإصدار، التحقق الذري، سجل الإلغاء) تحتاج مرحلة لاحقة قبل إعلان القبول النهائي. يُنصح باختبار RTL على سطح مكتب وهاتف ضيق، وسيناريو تغيير المرجع بعد إنشاء زيارة.
