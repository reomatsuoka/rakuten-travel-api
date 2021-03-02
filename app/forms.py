from django import forms

class SearchForm(forms.Form):
    travel_keyword = forms.CharField(label='キーワード', max_length=200, required=True)
