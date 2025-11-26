from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')), 
    path('api/tasks/', include('tasks.urls')),
]