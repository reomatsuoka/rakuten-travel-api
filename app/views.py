from django.shortcuts import render
from django.views.generic import View
import requests
import json
from .forms import SearchForm



REQUEST_URL = 'https://app.rakuten.co.jp/services/api/Travel/KeywordHotelSearch/20170426?format=json&applicationId=1077422512724458210'
def get_api_data(params):
    res = requests.get(REQUEST_URL, params)
    result = res.json()
    return result

class IndexView(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        return render(request, 'app/index.html', {
            'form': form
        })

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            params = {
                'format': 'json',
                'keyword': keyword,
            }

            result = get_api_data(params)
            travel_data = []
            for i in result:
                hotels = i['hotels'][0]
                hotel0 = hotels['hotel'][0]
                summary = hotel0['hotelBasicInfo']
                hotelname = summary['hotelName']
                image = summary['hotelImageUrl']
                review = summary['reviewAverage']
                plan = summary['planListUrl']
                minprice = summary['hotelMinCharge']
                hotel_detail = summary['hotelSpecial']
                address = summary['address1']
                address2 = summary['address2']

                hotel1 = hotels['hotel'][1]
                rating_info = hotel1['hotelRatingInfo']
                rating_service = rating_info['serviceAverage']
                rating_room = rating_info['roomAverage']
                rating_equipment = rating_info['equipmentAverage']
                rating_meal = rating_info['mealAverage']
                rating_location = rating_info['locationAverage']
                query = {
                    'hotelname': hotelname,
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
                travel_data.append(query)

            return render(request, 'app/travel.html', {
                'travel_data': travel_data,
                'keyword':keyword,
            })
        
        return render(request, 'app/index.html', {
        'form': 'form'
        })
        
        # form = SearchForm(request.POST or None)
        # results = get_api_data(params)
        # travel_data = []
        # for i in result:
        #     hotels = i['hotels']
        #     hotel = hotels['hotel']
        #     hotelname = hotel['hotelBasicInfo']['hotelName']
        #     query = {
        #         'hotelname' : hotelname,
        #     }
        #     travel_data.append(query)
        # return render(request, 'app/travel.html', {
        #     'travel_data': travel_data,
        #     'keyword': keyword,
        # })

    # return render(request, 'app/index.html', {
    #     'form': form,
    # })

        # return render(request, 'app/index.html', {
        #     'form': form,
        # })

    # def post(self, request, *args, **kwargs):
    #     form = SearchForm(request.POST or None)

    #     if form.is_valid():
    #         keyword = form.cleaned_data['keyword']
    #         params = {
    #             'keyword': keyword,
    #         }
    #         results = get_api_data(params)
    #         travel_data = []
    #         for i in result:
    #             hotels = i['hotels']
    #             hotel = hotels['hotel']
    #             hotelname = hotel['hotelBasicInfo']['hotelName']
    #             query = {
    #                 'hotelname' : hotelname,
    #             }
    #             travel_data.append(query)
    #         return render(request, 'app/travel.html', {
    #             'travel_data': travel_data,
    #             'keyword': keyword,
    #         })

    #     return render(request, 'app/index.html', {
    #         'form': form,
    #     })