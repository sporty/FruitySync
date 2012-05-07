#/usr/bin/env python
# coding=utf-8

from django import forms

class SignupForm(forms.Form):
    """
    ユーザー登録用フォーム
    """

    email = forms.EmailField(
                    required=True,
                    label='email address'
                )

    first_name = forms.CharField( 
                    required=True,
                    max_length=30,
                    label='UserName' 
                )
    
    last_name = forms.CharField( 
                    required=True,
                    max_length=30,
                    label='UserName' 
                )
    
    password = forms.CharField(
                    required=True,
                    max_length=128,
                    widget=forms.PasswordInput 
                )
    password_reply = forms.CharField(
                    required=True,
                    max_length=128,
                    widget=forms.PasswordInput 
                )
        
# EOF
