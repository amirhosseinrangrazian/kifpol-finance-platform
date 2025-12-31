from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Transaction, Budget, Goal, UserProfile, Category


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='ایمیل')
    first_name = forms.CharField(max_length=100, required=False, label='نام')
    last_name = forms.CharField(max_length=100, required=False, label='نام خانوادگی')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'username': 'نام کاربری',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password2'].label = 'تکرار رمز عبور'


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    class Meta:
        model = Category
        fields = ['name_fa', 'parent', 'icon', 'color']
        widgets = {
            'name_fa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام دسته‌بندی'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'bi-tag'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show parent categories (no nesting deeper than 1 level)
        self.fields['parent'].queryset = Category.objects.filter(
            Q(user=user) | Q(is_default=True),
            parent__isnull=True
        )

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'type', 'category', 'date']
        labels = {
            'title': 'عنوان',
            'amount': 'مبلغ (تومان)',
            'type': 'نوع',
            'category': 'دسته‌بندی',
            'date': 'تاریخ',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلا: خرید نان'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1403/10/01'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit', 'period']
        labels = {
            'category': 'دسته‌بندی',
            'limit': 'سقف بودجه (تومان)',
            'period': 'دوره',
        }
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-select'}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['title', 'target_amount', 'deadline']
        labels = {
            'title': 'عنوان هدف',
            'target_amount': 'مبلغ هدف (تومان)',
            'deadline': 'مهلت',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثلا: خرید آیفون'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '50000000'}),
            'deadline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1403/12/29'}),
        }


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=False, label='نام')
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'theme']
        labels = {
            'avatar': 'تصویر پروفایل',
            'theme': 'رنگ پوسته',
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
        }
