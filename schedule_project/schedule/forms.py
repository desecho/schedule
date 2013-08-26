# -*- coding: utf8 -*-
from django import forms
from schedule.models import Student
from django.conf import settings

# old_build_attrs = Widget.build_attrs
# def build_attrs(self, extra_attrs=None, **kwargs):
#   attrs = old_build_attrs(self, extra_attrs, **kwargs)

#   if self.is_required and type(self) not in (AdminFileWidget,HiddenInput, FileInput) and "__prefix__" not in attrs["name"]:
#     attrs["required"] = "required"

#   return attrs

# Widget.build_attrs = build_attrs



def text_widget():
    return forms.TextInput(attrs={'required': ''})

def date_widget():
    return forms.DateInput(format=settings.DATE_FORMAT, attrs={'required': ''})

def email_widget():
    return forms.TextInput(attrs={'type': 'email'})

def multiple_select_widget():
    return forms.SelectMultiple(attrs={'required': ''})

def select_widget():
    return forms.Select(attrs={'required': ''})


class StudentRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentRegisterForm, self).__init__(*args, **kwargs)
        self.fields['subjects'].help_text = ''

    class Meta:
        model = Student
        widgets = {
            'name': text_widget(),
            'last_name': text_widget(),
            'middle_name': text_widget(),
            'phone': text_widget(),
            'parents_phone': text_widget(),
            'birthday': date_widget(),
            'email': email_widget(),
            'subjects': multiple_select_widget(),
            'office': select_widget(),
            'passport_number': text_widget(),
            'passport_authority': text_widget(),
            'passport_issued_date': date_widget(),
            'passport_unit': text_widget(),
            'level': forms.TextInput(attrs={
                'pattern': '\d',
                'maxlength': '1',
                'min': '0',
                'max': '5',
                'required': ''}),
        }