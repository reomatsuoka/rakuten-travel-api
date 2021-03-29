from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .models import Hotel, Favorite, Area
import requests
import json
from .forms import SearchForm


REQUEST_VACANCY_URL = 'https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_URL = 'https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_DETAIL_URL = 'https://app.rakuten.co.jp/services/api/Travel/HotelDetailSearch/20170426?format=json&applicationId=1077422512724458210'

json_file = open('app/areacode.json', 'r')
# JSONとして読み込む
json_obj  = json.load(json_file)


def get_api_data(params):
    res = requests.get(REQUEST_URL, params)
    result = res.json()
    return result


def get_api_detail_data(params):
    res = requests.get(REQUEST_DETAIL_URL, params)
    result = res.json()
    return result


def paginate_queryset(request, queryset, count):
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['middleClasses'] = json_obj.objects.all()
        return context
class IndexView(View, LoginRequiredMixin):
    login_url = '/accounts/login/'
    
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        # JSONから下記を作れば完成
        middleClassCodeData = []
        smallClassCode = []
        smallClassName = []

        for i in json_obj['middleClasses']:
            middleClassCodeData.append(i['middleClass'][0]['middleClassCode'])
            small_classes = i['middleClass'][1]['smallClasses']
            # print(small_classes)
            for j in small_classes:
                smallClassCode.append(j['smallClass'][0]['smallClassCode'])
                smallClassName.append(j['smallClass'][0]['smallClassName'])

        
                

            for middleClassCode in middleClassCodeData:
                # print(middleClassCode)
                category_data = {
                    middleClassCode : [
                        {
                            "pk": smallClassCode,
                            "name": smallClassName,
                        },
                    ],
                }
                # print(category_data)
                return render(request, 'app/index.html', {
                    'form': form,
                    'category_data': json.dumps(category_data)
                })

class SearchView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        checkin_date = request.GET['checkin_date']
        checkout_date = request.GET['checkout_date']
        middle_class_name = request.GET['middle_class_name']
        small_class_name = request.GET['small_class_name']
        adult_num = request.GET['adult_num']
        room_num = request.GET['room_num']
        min_charge = request.GET['min_charge']
        max_charge = request.GET['max_charge']

        params = {
            'checkinDate': checkin_date,
            'checkoutDate': checkout_date,
            'largeClassCode': "japan",
            'middleClassCode': middle_class_name,
            'smallClassCode': small_class_name,
            'adultNum' : adult_num,
            'roomNum': room_num,
            'minCharge': min_charge,
            'maxCharge': max_charge,
        }
        result = get_api_data(params)
        if 'hotels' not in result:
            return render(request, 'app/error.html')

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
            dpPlanListUrl = summary['dpPlanListUrl']
            reviewUrl = summary['reviewUrl']

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
                'dpPlanListUrl': dpPlanListUrl,
                'reviewUrl': reviewUrl,
            }
            # データがない宿泊施設を除外する
            if not isinstance(review, float):
                continue
            # reviewが4.0以上のみ表示する
            if review >= 4.0:
                travel_data.append(query)
        # 降順に並び替え
        travel_data = sorted(travel_data, key=lambda x: x['review'], reverse=True)
        total_hit_count = len(travel_data)
        page_obj = paginate_queryset(request, travel_data, 10)

        return render(request, 'app/travel.html', {
            'travel_data': page_obj.object_list,
            'total_hit_count':total_hit_count,
            'page_obj': page_obj,
        })

@login_required
def addFavorite(request, id):
    favorite_data = Favorite.objects.get(user=request.user)
    # 第2引数は使わないため　”_”を入れる。
    hotel_data, _ = Hotel.objects.get_or_create(number=id)
    if not hotel_data in favorite_data.hotelno.all():
        favorite_data.hotelno.add(hotel_data)
        favorite_data.save()

    return redirect('favorite')

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
        userReview = summary['userReview']
        dpPlanListUrl = summary['dpPlanListUrl']
        reviewUrl = summary['reviewUrl']
        telephoneNo = summary['telephoneNo']
        access = summary['access']
        parkingInformation = summary['parkingInformation']
        nearestStation = summary['nearestStation']
        roomImageUrl = summary['roomImageUrl']
        hotelMapImageUrl = summary['hotelMapImageUrl']

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
            'userReview': userReview,
            'dpPlanListUrl': dpPlanListUrl,
            'reviewUrl': reviewUrl,
            'telephoneNo': telephoneNo,
            'access': access,
            'parkingInformation': parkingInformation,
            'nearestStation': nearestStation,
            'roomImageUrl': roomImageUrl,
            'hotelMapImageUrl': hotelMapImageUrl,
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

@login_required
def removeFavorite(request, id):
    favorite_data = Favorite.objects.get(user=request.user)
    hotelNo_data, _ = Hotel.objects.get_or_create(number=id)
    favorite_data.hotelno.remove(hotelNo_data)
    return redirect('favorite')
