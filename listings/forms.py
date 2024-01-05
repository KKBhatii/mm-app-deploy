from django import forms
from django.core.validators import FileExtensionValidator

# to allow multiple uploads
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    

# form to list new item
class ListItemForm(forms.Form):
    # image validator
    image_file_validator = FileExtensionValidator(
        allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp"],
        message="Only image files (jpg, jpeg, png, gif, bmp) are allowed."
    )
    CATEGORY_CHOICES=[
        ("Cars", "Cars"),
        ("Mobile phones", "Mobile phones"),
        ("Electronics", "Electronics"),
        ("Furniture", "Furniture"),
        ("Others", "Others")]
    title=forms.CharField(required=True,max_length=50,)
    description=forms.CharField(required=False,widget=forms.Textarea(attrs={"placeholder":"Describe your item..."}))
    category=forms.ChoiceField(required=True,choices=CATEGORY_CHOICES)
    price=forms.IntegerField(required=True)
    images=MultipleFileField(required=False,widget=MultipleFileInput(attrs={"multiple":True,"accept":"image/*", "hidden":True}))

    # to make sure that user can upload a max of 5 images
    def clean_images(self):
        images = self.cleaned_data.get("images")
        if images:
            if len(images) > 5:
                raise forms.ValidationError("Maximum 5 images allowed!")
        return images


