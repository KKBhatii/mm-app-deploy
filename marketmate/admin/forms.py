from django import forms

# form to create new user
class CreateUserForm(forms.Form):
    name=forms.CharField(label=None, widget=forms.TextInput(attrs={"placeholder":"Enter a Name..."}))
    email=forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder":"Enter a Email Address..."}))
    password=forms.CharField(label=None, widget=forms.PasswordInput(attrs={"placeholder":"Enter a Password..."}))
    confirm_password=forms.CharField(label=None,help_text="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder":"Re-enter Password..."}))
