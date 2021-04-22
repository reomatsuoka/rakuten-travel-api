from django.urls import path
from app import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('error/', views.IndexView.as_view(), name='error'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('like/', views.LikeView, name='like'),
    path('detail/<str:hotelno>', views.DetailView.as_view(), name='detail'),
    path('favorite/', views.FavoriteView.as_view(), name='favorite'),
    path('addfavorite/<id>', views.addFavorite, name='addfavorite'),
    path('removefavorite/<id>', views.removeFavorite, name='removefavorite'),
]