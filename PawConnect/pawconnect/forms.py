from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from pawconnect.models import Profile, RehomeQuizResult, AdoptQuizResult, MarketItem

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id': 'id_username'}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'id': 'id_password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):

    username   = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id': 'id_username'}))
    password1  = forms.CharField(max_length=200,
                                 label='Password', 
                                 widget=forms.PasswordInput(attrs={'id': 'id_password'}))
    password2  = forms.CharField(max_length=200,
                                 label='Confirm',  
                                 widget=forms.PasswordInput(attrs={'id': 'id_confirm_password'}))
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput(attrs={'id': 'id_email'}))
    first_name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id': 'id_first_name'}))
    last_name  = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id': 'id_last_name'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

MAX_UPLOAD_SIZE = 2500000

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( 'bio', 'picture', 'city')
        widgets = {
            'bio': forms.Textarea(attrs={'id': 'id_bio_input_text', 'rows': 3}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture'}),
            'city': forms.TextInput(attrs={'id': 'id_city'})
        }
        labels = {
            'bio': '',
            'picture': 'Profile Picture',
            'city': 'City'
        }

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')  # Use .get() to handle None case
        if picture:
            if not hasattr(picture, 'content_type'):
                raise forms.ValidationError('You must upload a picture')
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            if picture.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


# class AdoptQuizForm(forms.ModelForm):
#     class Meta:
#         model = AdoptQuizResult
#         fields = ['species', 'living_situation', 'hours_away', 'pet_size', 'pet_experience', 'pet_energy_level', 'specific_training', 'medical_expenses_plan', 'adoption_reason']

class MarketItemForm(forms.ModelForm):
    class Meta:
        model = MarketItem
        fields = ['title', 'description', 'price', 'image', 'quantity']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Item title'}),
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 5, 'placeholder': 'Item description'}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'image': forms.FileInput(attrs={'id': 'id_item_image'}),
        }
        labels = {
            'image': 'Item Image',
        }
    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture or not hasattr(picture, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture

class AddBalanceForm(forms.Form):
    amount = forms.DecimalField(label='Amount', max_digits=6, decimal_places=2, min_value=0.01)