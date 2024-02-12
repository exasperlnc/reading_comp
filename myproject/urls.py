"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from reading_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', views.upload_document, name='upload_document'),
    path('document/<int:document_id>/', views.view_document, name='view_document'),
    path('submit-answer/', views.submit_answer, name='submit_answer'),
    path('answer-success/', views.answer_success, name='answer_success'),

]

