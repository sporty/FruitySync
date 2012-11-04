#/usr/bin/env python
# coding=utf-8

from django import forms
from django.contrib.auth.models import User


class SignupForm(forms.Form):
    """
    ユーザー登録用フォーム
    """

    email = forms.EmailField(
                    required=True,
                    label='email address',
                    widget=forms.HiddenInput
                )

    first_name = forms.CharField( 
                    required=True,
                    max_length=30,
                    label=u'姓' 
                )
    
    last_name = forms.CharField( 
                    required=True,
                    max_length=30,
                    label=u'名' 
                )
    
    password = forms.CharField(
                    required=True,
                    max_length=128,
                    widget=forms.PasswordInput,
                    label=u'パスワード' 
                )
    password_reply = forms.CharField(
                    required=True,
                    max_length=128,
                    widget=forms.PasswordInput,
                    label=u'パスワード再入力' 
                )

    def clean(self):
        """
        is_validが呼ばれたときの処理
        """

        cleaned_data = super(SignupForm, self).clean()

        email = cleaned_data.get("email")
        try:
            account = User.objects.get(username=email)
            if account:
                raise forms.ValidationError(u"指定されたメールアドレスは既に登録済みです")
        except:
            pass

        password_1 = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_reply")
        if not password_1 == password_2:
            raise forms.ValidationError(u"パスワード入力に誤りがあります")

        # Always return the full collection of cleaned data.
        return cleaned_data       

# EOF
