from django import forms
from .models import Area
import json
import datetime

json_file = open('app/areacode.json', 'r')
# JSONとして読み込む
json_obj  = json.load(json_file)

class SearchForm(forms.Form):
    prefecture_choice = {}
    city_choice = {}
    for i in json_obj['middleClasses']:
        prefecture_choice[i['middleClass'][0]['middleClassCode']] = i['middleClass'][0]['middleClassName']
        small_classes = i['middleClass'][1]['smallClasses']
        for j in small_classes:
            city_choice[j['smallClass'][0]['smallClassCode']] = j['smallClass'][0]['smallClassName']

    today = datetime.date.today()
    plus_date = datetime.timedelta(days=1)
    tomorrow = today + plus_date
    checkin_date = forms.DateField(label='チェックイン日', required=True, widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=['%Y-%m-%d'], initial=today)
    stay_days = forms.ChoiceField(label='宿泊日数', choices=[(x, x) for x in range(1, 10)])
    checkout_date = forms.DateField(label='チェックアウト日', required=True, widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=['%Y-%m-%d'], initial=tomorrow)
    middle_class_name = forms.ChoiceField(label='都道府県', widget=forms.Select, choices=list(prefecture_choice.items()))
    small_class_name = forms.ChoiceField(label='市区郡名', widget=forms.Select, choices=list(city_choice.items()))
    adult_num = forms.ChoiceField(label='大人の人数', choices=[(x, x) for x in range(1, 10)])
    room_num = forms.ChoiceField(label='部屋数', choices=[(x, x) for x in range(1, 10)])
    min_charge = forms.ChoiceField(
        label='下限金額',
        required=False,
        choices=[(0,'下限なし'),(1000,1000),(2000,2000),(3000,3000),(4000,4000),(5000,5000),(6000,6000),(7000,7000),(8000,8000),(9000,9000),(10000,10000),(12000,12000),(14000,14000),(16000,16000),(18000,18000),(20000,20000),(30000,30000),(40000,40000),(50000,50000)]
    )
    max_charge = forms.ChoiceField(
        label='上限金額',
        required=False,
        choices=[(999999999,'上限なし'),(1000,1000),(2000,2000),(3000,3000),(4000,4000),(5000,5000),(6000,6000),(7000,7000),(8000,8000),(9000,9000),(10000,10000),(12000,12000),(14000,14000),(16000,16000),(18000,18000),(20000,20000),(30000,30000),(40000,40000),(50000,50000)]
    )



