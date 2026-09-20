from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth
urlpatterns=[path('admin/',admin.site.urls),path('login/',auth.LoginView.as_view(template_name='login.html'),name='login'),path('logout/',auth.LogoutView.as_view(),name='logout'),path('',include('core.urls'))]
