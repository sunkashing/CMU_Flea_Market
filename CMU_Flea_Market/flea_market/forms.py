from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from haystack.forms import SearchForm
from flea_market.models import *

MAX_UPLOAD_SIZE = 2500000
CAT = [('Clothes', 'Clothes'),
       ('Electronic Devices', 'Electronic Devices'),
       ('Cars', 'Cars'),
       ('Books', 'Books'),
       ('House Leasing', 'House Leasing'),
       ]


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'id': 'id_username', 'class': 'form-input'}), help_text='account_box', label='Username')
    password = forms.CharField(
        max_length=20, widget=forms.PasswordInput(
            attrs={'id': 'id_password', 'class': 'form-input'}), help_text='lock_outline', label='Password')

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise forms.ValidationError('Invalid username or password')

        return cleaned_data


class ItemForm(forms.Form):
    itemCategory = forms.ChoiceField(
        widget=forms.Select(attrs={'id': 'id_product_category', 'class': 'form-control form-control-md', 'oninput': 'previewCategory()'}),
        choices=CAT, help_text='category', label="Please choose a category")
    itemPicture = forms.FileField(
        widget=forms.FileInput(attrs={'id': 'id_product_picture', 'class': 'form-control-md',
                                      'oninput': 'previewFile()', 'multiple': True, 'style': 'opacity: 0;'}),
        help_text='image', label="Please upload a picture")
    itemName = forms.CharField(
        max_length=40, widget=forms.TextInput(
            attrs={'id': 'id_product_name', 'class': 'form-control', 'oninput': 'previewName()'}), help_text='edit', label="Please enter a name")
    itemPrice = forms.DecimalField(
        widget=forms.TextInput(
            attrs={'id': 'id_product_price', 'class': 'form-control', 'oninput': 'previewPrice()'}), help_text='attach_money',
        label="Please enter a price")
    itemStatus = forms.DecimalField(widget=forms.TextInput(attrs={'id': 'id_product_status',
                                                                  'class': 'form-control-md custom-range',
                                                                  'type': 'range', 'min': '0',
                                                                  'max': '5', 'step': '0.5',
                                                                  'oninput': 'previewStatus()'}),
                                    help_text='build', label='Product Status')

    itemDescription = forms.CharField(
        max_length=100, widget=forms.Textarea(
            attrs={'id': 'id_product_description', 'class': 'md-textarea form-control',
                   'rows': '4', 'resize': 'none', 'oninput': 'previewDescription()'}),
        help_text='comment',
        label='Please describe the item')

    def clean_picture(self):
        picture = self.cleaned_data['itemPicture']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'id': 'id_username', 'class': 'form-input'}), help_text='account_box', label='Username')
    password = forms.CharField(
        max_length=20, widget=forms.PasswordInput(
            attrs={'id': 'id_password', 'class': 'form-input'}), help_text='lock_outline', label='Password')
    confirm_password = forms.CharField(
        max_length=20, widget=forms.PasswordInput(
            attrs={'id': 'id_confirm_password', 'class': 'form-input'}), help_text='lock', label='Confirm Password')
    email = forms.CharField(
        max_length=50, widget=forms.EmailInput(
            attrs={'id': 'id_email', 'class': 'form-input'}), help_text='email', label='Email')
    first_name = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'id': 'id_first_name', 'class': 'form-input'}), help_text='arrow_left', label='First Name')
    last_name = forms.CharField(
        max_length=20, widget=forms.TextInput(
            attrs={'id': 'id_last_name', 'class': 'form-input'}), help_text='arrow_right', label='Last Name')
    birthday = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'id': 'id_birthday', 'class': 'form-input', 'type': 'date'}), help_text='cake', label='Birthday')
    geo_location = forms.CharField(
        max_length=40, widget=forms.TextInput(
            attrs={'id': 'id_geo_location', 'class': 'form-input'}), help_text='home', label='City')
    preferences = forms.CharField(
        max_length=40, widget=forms.TextInput(
            attrs={'id': 'id_preferences', 'class': 'form-input'}), help_text='star', label='Preferences')

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Password not match')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError('Username is existed, try another one')
        return username


class UserForm(forms.ModelForm):
    class Meta:
        model = Customer
        widgets = {'customer_log': forms.Textarea(
            attrs={'id': 'customer_log_text', 'class': "form-control bg-graylight border-0 font-weight-bold"}),
            'picture': forms.FileInput(attrs={'id': 'id_profile_picture'}),
        }
        fields = ('picture', 'customer_log')

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture


class MySearchForm(SearchForm):
    q = forms.CharField(
        max_length=20, required=False, widget=forms.TextInput(
            attrs={'type': 'search', 'id': 'search-input',
                   'class': 'form-control bg-graylight border-0 font-weight-bold',
                   'placeholder': 'Search...', 'autocomplete': 'off', 'style': 'width: 600px; outline: none; border-radius: 20px'}))

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(MySearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        return sqs
