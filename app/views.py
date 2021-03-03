from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
import requests
import json
from .forms import SearchForm




REQUEST_URL = 'https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426?format=json&applicationId=1077422512724458210'
def get_api_data(params):
    res = requests.get(REQUEST_URL, params)
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
                'format': 'json',
                'keyword': keyword,
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
            'hotelno': hotelno,
        }
        
        result = get_api_data(params)
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