from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .models import Hotel, Favorite, Area
import requests
import json
from .forms import SearchForm


REQUEST_VACANCY_URL = 'https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_URL = 'https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_DETAIL_URL = 'https://app.rakuten.co.jp/services/api/Travel/HotelDetailSearch/20170426?format=json&applicationId=1077422512724458210'
REQUEST_RANKING_URL = 'https://app.rakuten.co.jp/services/api/Travel/HotelRanking/20170426?format=json&applicationId=1077422512724458210'

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

def get_api_ranking_data(params):
    res = requests.get(REQUEST_RANKING_URL, params)
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

class IndexView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)

        # JSONから下記を作れば完成
        category_data = {}
        for i in json_obj['middleClasses']:
            middleClassCodeData = i['middleClass'][0]['middleClassCode']
            small_classes = i['middleClass'][1]['smallClasses']
            small_class = []
            for j in small_classes:
                smallClassCode = j['smallClass'][0]['smallClassCode']
                smallClassName = j['smallClass'][0]['smallClassName']
                small_class.append({
                    "pk": smallClassCode, 
                    "name": smallClassName
                })
                category_data[middleClassCodeData] = small_class

        params = {
            'genre': 'onsen'
        }
        result = get_api_ranking_data(params)
        ranking_data = []
        for i in result['Rankings']:
            ranking = i['Ranking']
            title = ranking['title']
            hotels = ranking['hotels']
            ranking_info = title

            for j in hotels:
                hotel = j['hotel']
                rank = hotel['rank']
                hotelName = hotel['hotelName']
                middleClassName = hotel['middleClassName']
                hotelImageUrl = hotel['hotelImageUrl']
                hotelNo = hotel['hotelNo']

                query = {
                    'rank': rank,
                    'hotelName': hotelName,
                    'middleClassName': middleClassName,
                    'hotelImageUrl': hotelImageUrl,
                    'hotelNo': hotelNo,
                }
                for a in range(2,7):
                    if rank == a:
                        ranking_data.append(query)
                        break

        return render(request, 'app/index.html', {
            'form': form,
            'category_data': json.dumps(category_data),
            'ranking_info': ranking_info,
            'ranking_data': ranking_data,
        })

class SearchView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        form = SearchForm(request.POST or None)
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
            hotelname_replace = hotelname.replace('　', '')
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
                'hotelname_replace': hotelname_replace,
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
    # 第2引数は使わないため”_”を入れる。
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

def LikeView(request):
    if request.method =="POST":
        hotel_data, _ = Hotel.objects.get_or_create(number=request.POST.get('hotelno'))
        favorite_data = Favorite.objects.get(user=request.user)
        if not hotel_data in favorite_data.hotelno.all():
            favorite_data.hotelno.add(hotel_data)
            favorite_data.save()
            favo = True
        else:
            favorite_data.hotelno.remove(hotel_data)
            favorite_data.save()
            favo = False

        hotel_list = []
        for i in favorite_data.hotelno.all():
            hotel_list.append(i.number)

        context={
            'hotel_list': hotel_list,
            'hotelno': request.POST.get('hotelno'),
            'favo': favo,
        }

    if request.is_ajax():
        return JsonResponse(context)


class FavoriteView(View, LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        #userを取得or作成する。
        favorite_data, _ = Favorite.objects.get_or_create(user=request.user)
        # userに結びつくhotelnoを取得する
        hotelno = favorite_data.hotelno.all()
        # hotelnoが存在すればお気に入りにデータを出力。
        if hotelno.exists():
            hotel_data = []
            for hotelno_data in favorite_data.hotelno.all():
                params = {
                    'hotelNo': hotelno_data.number,
                }
                result = get_api_detail_data(params)
                hotel0 = result['hotels'][0]['hotel'][0]
                summary = hotel0['hotelBasicInfo']
                hotelname = summary['hotelName']
                hotelname_replace = hotelname.replace('　', '')
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
                    'hotelname_replace': hotelname_replace,
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
                }
                hotel_data.append(query)

            return render(request, 'app/favorite.html',{
                'hotel_data': hotel_data,
            })
        # hotelnoがなければ”該当なし”と出力する。
        else:
            return render(request, 'app/notexists.html')

@login_required
def removeFavorite(request, id):
    favorite_data = Favorite.objects.get(user=request.user)
    hotelNo_data, _ = Hotel.objects.get_or_create(number=id)
    favorite_data.hotelno.remove(hotelNo_data)
    return redirect('favorite')
