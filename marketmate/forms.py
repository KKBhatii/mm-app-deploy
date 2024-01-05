from django import forms


# login form for admin
class AdminLoginForm(forms.Form):
    email=forms.EmailField(required=True,widget=forms.EmailInput(attrs={"placeholder":"Enter your Email.."}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Enter your Password.."}))