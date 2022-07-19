from django import forms

class UserInputForm(forms.Form):
    initial_place = forms.CharField(max_length=20, required=True)
    commands = forms.CharField(widget=forms.Textarea(attrs={"rows":10, "cols":20}), required=False)