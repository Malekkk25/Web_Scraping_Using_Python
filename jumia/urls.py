
from . import views
from django.urls import path,include

urlpatterns = [
    path('filter/',views.filter ,name= 'home'),
    
]
