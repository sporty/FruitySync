#/usr/bin/env python
# coding=utf-8

from django import forms

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
        
# EOF
