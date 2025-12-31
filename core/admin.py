from django.contrib import admin
from .models import Category, Transaction, Budget, Goal, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_fa', 'icon', 'is_default', 'user']
    list_filter = ['is_default']
    search_fields = ['name', 'name_fa']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'type', 'category', 'date', 'user']
    list_filter = ['type', 'category', 'user']
    search_fields = ['title']
    date_hierarchy = 'created_at'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'limit', 'period', 'user']
    list_filter = ['period', 'user']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_amount', 'current_amount', 'deadline', 'user']
    list_filter = ['user']
    search_fields = ['title']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme']
    list_filter = ['theme']
