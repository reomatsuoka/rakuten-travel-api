from django.urls import path
from app import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<str:hotelno>', views.DetailView.as_view(), name='detail'),
    path('favorite/<int:pk>/', views.FavoriteView.as_view(), name='favorite'),
]