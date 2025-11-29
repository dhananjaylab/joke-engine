from django.urls import path
from . import views

urlpatterns = [
    path('', views.giggle_search, name='giggle_search'),
    path('history/', views.giggle_history, name='giggle_history'),
    path('delete/<int:pk>', views.delete_joke, name='delete_joke'),
    path('heckle/', views.heckle_station, name='heckle_station'),
    path('explain/<int:pk>/', views.explain_joke, name='explain_joke'),
    path('meme/<int:pk>/', views.generate_meme, name='generate_meme'),
]
