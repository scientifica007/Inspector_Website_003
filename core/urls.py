from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard,name='dashboard'),path('visits/new/',views.visit_new,name='visit_new'),path('visits/<int:pk>/',views.visit_detail,name='visit_detail'),path('visits/<int:pk>/complete/',views.complete,name='complete'),path('visits/<int:pk>/export/',views.export_visit,name='export'),path('visits/<int:pk>/guides/<int:guide_id>/apply/',views.apply_guide_view,name='apply_guide'),path('references/',views.references,name='references'),path('institutions/',views.institutions,name='institutions')]
