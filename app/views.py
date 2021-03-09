from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Hotel, Favorite
import requests
import json
from .forms import SearchForm




REQUEST_URL = 'https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_DETAIL_URL = 'https://app.rakuten.co.jp/services/api/Travel/HotelDetailSearch/20170426?format=json&applicationId=1077422512724458210'
def get_api_data(params):
    res = requests.get(REQUEST_URL, params)
    result = res.json()
    return result

def get_api_detail_data(params):
    res = requests.get(REQUEST_DETAIL_URL, params)
    result = res.json()
    return result

class IndexView(View, LoginRequiredMixin):
    login_url = '/accounts/login/'
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        return render(request, 'app/index.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        if form.is_valid():
            keyword = form.cleaned_data['travel_keyword']
            params = {
                'keyword': keyword,
                # 'hits': 5,
            }

            result = get_api_data(params)
            travel_data = []
            for i in result['hotels']:

                hotel0 = i['hotel'][0]
                summary = hotel0['hotelBasicInfo']
                hotelname = summary['hotelName']
                hotelno = summary['hotelNo']
                image = summary['hotelImageUrl']
                review = summary['reviewAverage']
                plan = summary['planListUrl']
                minprice = summary['hotelMinCharge']
                hotel_detail = summary['hotelSpecial']
                address = summary['address1']
                address2 = summary['address2']

                hotel1 = i['hotel'][1]
                rating_info = hotel1['hotelRatingInfo']
                rating_service = rating_info['serviceAverage']
                rating_room = rating_info['roomAverage']
                rating_equipment = rating_info['equipmentAverage']
                rating_meal = rating_info['mealAverage']
                rating_location = rating_info['locationAverage']
                query = {
                    'hotelname': hotelname,
                    'hotelno': hotelno,
                    'image': image,
                    'review': review,
                    'plan': plan,
                    'minprice': minprice,
                    'hotel_detail': hotel_detail,
                    'address':address,
                    'address2': address2,
                    'rating_service': rating_service,
                    'rating_room': rating_room,
                    'rating_equipment': rating_equipment,
                    'rating_meal': rating_meal,
                    'rating_location': rating_location,
                }
                # データがない宿泊施設を除外する
                if not isinstance(review, float):
                    continue
                # reviewが4.0以上のみ表示する
                if review >= 4.0:
                    travel_data.append(query)
            # 降順に並び替え
            travel_data = sorted(travel_data, key=lambda x: x['review'], reverse=True)

            return render(request, 'app/travel.html', {
                'travel_data': travel_data,
                'keyword':keyword,
            })
        
        return render(request, 'app/index.html', {
        'form': 'form'
        })
        
class DetailView(View):
    def get(self, request, *args, **kwargs):
        hotelno = self.kwargs['hotelno']
        params = {
            'hotelNo': int(hotelno),
        }

        result = get_api_detail_data(params)
        hotel0 = result['hotels'][0]['hotel'][0]
        summary = hotel0['hotelBasicInfo']
        hotelname = summary['hotelName']
        hotelno = summary['hotelNo']
        image = summary['hotelImageUrl']
        review = summary['reviewAverage']
        reviewCount = summary['reviewCount']
        plan = summary['planListUrl']
        minprice = summary['hotelMinCharge']
        hotel_detail = summary['hotelSpecial']
        address = summary['address1']
        address2 = summary['address2']

        hotel1 = result['hotels'][0]['hotel'][1]
        rating_info = hotel1['hotelRatingInfo']
        rating_service = rating_info['serviceAverage']
        rating_room = rating_info['roomAverage']
        rating_equipment = rating_info['equipmentAverage']
        rating_meal = rating_info['mealAverage']
        rating_location = rating_info['locationAverage']
        travel_data = {
            'hotelname': hotelname,
            'hotelno': hotelno,
            'image': image,
            'review': review,
            'reviewCount': reviewCount,
            'plan': plan,
            'minprice': minprice,
            'hotel_detail': hotel_detail,
            'address':address,
            'address2': address2,
            'rating_service': rating_service,
            'rating_room': rating_room,
            'rating_equipment': rating_equipment,
            'rating_meal': rating_meal,
            'rating_location': rating_location,
            'average': float(review) * 20,
        }

        return render(request, 'app/detail.html', {
            'travel_data': travel_data,
        })

class FavoriteView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        # hotelnoの情報を引き出す。
        favorite_data = Favorite.objects.get(user=request.user)
        hotelno = favorite_data.hotelno
        hotel_data = []
        for hotelno_data in favorite_data.hotelno.all():
            params = {
                'hotelNo': hotelno_data.number,
            }
            result = get_api_detail_data(params)
            hotel0 = result['hotels'][0]['hotel'][0]
            summary = hotel0['hotelBasicInfo']
            hotelname = summary['hotelName']
            hotelno = summary['hotelNo']
            image = summary['hotelImageUrl']
            review = summary['reviewAverage']
            reviewCount = summary['reviewCount']
            plan = summary['planListUrl']
            minprice = summary['hotelMinCharge']
            hotel_detail = summary['hotelSpecial']
            address = summary['address1']
            address2 = summary['address2']

            hotel1 = result['hotels'][0]['hotel'][1]
            rating_info = hotel1['hotelRatingInfo']
            rating_service = rating_info['serviceAverage']
            rating_room = rating_info['roomAverage']
            rating_equipment = rating_info['equipmentAverage']
            rating_meal = rating_info['mealAverage']
            rating_location = rating_info['locationAverage']
            query = {
                'hotelname': hotelname,
                'hotelno': hotelno,
                'image': image,
                'review': review,
                'reviewCount': reviewCount,
                'plan': plan,
                'minprice': minprice,
                'hotel_detail': hotel_detail,
                'address':address,
                'address2': address2,
                'rating_service': rating_service,
                'rating_room': rating_room,
                'rating_equipment': rating_equipment,
                'rating_meal': rating_meal,
                'rating_location': rating_location,
                'average': float(review) * 20,
            }
            hotel_data.append(query)

        return render(request, 'app/favorite.html',{
            'hotel_data': hotel_data,
        })