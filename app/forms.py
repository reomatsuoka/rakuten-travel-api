from django import forms
from .models import Area
import json

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

    checkin_date = forms.DateField(label='チェックイン日', required=True, widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=['%Y-%m-%d'])
    checkout_date = forms.DateField(label='チェックアウト日', required=True, widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=['%Y-%m-%d'])
    middle_class_name = forms.ChoiceField(label='都道府県', widget=forms.Select, choices=list(prefecture_choice.items()))
    small_class_name = forms.ChoiceField(label='市区郡名', widget=forms.Select, choices=list(city_choice.items()))
    adult_num = forms.ChoiceField(label='大人の人数', choices=[(x, x) for x in range(1, 10)])
    room_num = forms.ChoiceField(label='部屋数', choices=[(x, x) for x in range(1, 10)])
    min_charge = forms.CharField(label='下限金額', required=False)
    max_charge = forms.CharField(label='上限金額', required=False)




