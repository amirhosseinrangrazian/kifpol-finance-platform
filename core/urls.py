from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/export/', views.export_transactions, name='export_transactions'),
    path('transactions/import/', views.import_transactions, name='import_transactions'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    path('api/analytics-data/', views.analytics_data, name='analytics_data'),
    
    # Categories
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Budget
    path('budget/', views.budget, name='budget'),
    path('budget/save/', views.save_budget, name='save_budget'),
    path('budget/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
    
    # Goals
    path('goals/', views.goals, name='goals'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/<int:pk>/deposit/', views.deposit_goal, name='deposit_goal'),
    path('goals/<int:pk>/delete/', views.delete_goal, name='delete_goal'),
    path('goals/<int:pk>/advice/', views.goal_advice, name='goal_advice'),
    
    # Advisor
    path('advisor/', views.advisor, name='advisor'),
    path('advisor/ask/', views.advisor_ask, name='advisor_ask'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
]
