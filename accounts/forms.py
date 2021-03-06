from django import forms
from allauth.account.forms import SignupForm

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30, label='名')
    # null=True,blank=Trueとの違いは？ forms.pyでは使えない。
    department = forms.CharField(max_length=30, label='所属', required=False)
    image = forms.ImageField(label='イメージ画像', required=False)

class SignupUserForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30, label='名')

    def save(self, request):
        user = super(SignupUserForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user