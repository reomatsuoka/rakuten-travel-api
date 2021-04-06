from django.urls import path
from app import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # indexViewとSearchViewを分けるのはなぜ？
    path('search/', views.SearchView.as_view(), name='search'),
    path('detail/<str:hotelno>', views.DetailView.as_view(), name='detail'),
    path('favorite/', views.FavoriteView.as_view(), name='favorite'),
    path('addfavorite/<id>', views.addFavorite, name='addfavorite'),
    path('addfavorite2/<id>', views.addFavorite2, name='addfavorite2'),
    path('removefavorite/<id>', views.removeFavorite, name='removefavorite'),
]