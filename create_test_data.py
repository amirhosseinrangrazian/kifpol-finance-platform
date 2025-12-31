"""
Script to create test data for KifPool
Run with: python manage.py shell < create_test_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kifpol.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Category, Transaction, Budget, Goal, UserProfile

# Create admin user if not exists
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@kifpool.com', 'admin123')
    print("Admin user created: admin / admin123")
else:
    admin = User.objects.get(username='admin')
    print("Admin user already exists")

# Make sure profile exists
profile, _ = UserProfile.objects.get_or_create(user=admin)

# Create default categories
categories_data = [
    ('Food', 'خوراکی', 'bi-cup-hot'),
    ('Transport', 'حمل و نقل', 'bi-car-front'),
    ('Shopping', 'خرید', 'bi-bag'),
    ('Housing', 'مسکن', 'bi-house'),
    ('Salary', 'حقوق', 'bi-briefcase'),
    ('Health', 'سلامت', 'bi-heart-pulse'),
    ('Income', 'درآمد', 'bi-wallet2'),
    ('Other', 'سایر', 'bi-three-dots'),
]

categories = {}
for name, name_fa, icon in categories_data:
    cat, _ = Category.objects.get_or_create(
        name=name,
        is_default=True,
        defaults={'name_fa': name_fa, 'icon': icon}
    )
    categories[name] = cat

print(f"Created {len(categories)} categories")

# Create test transactions
transactions_data = [
    ('حقوق ماهانه', 25000000, 'INCOME', '1403/10/01', 'Salary'),
    ('خرید هایپراستار', 1250000, 'EXPENSE', '1403/10/02', 'Shopping'),
    ('اسنپ', 85000, 'EXPENSE', '1403/10/03', 'Transport'),
    ('کافه لمیز', 120000, 'EXPENSE', '1403/10/04', 'Food'),
    ('اجاره خانه', 8000000, 'EXPENSE', '1403/10/05', 'Housing'),
    ('واریز سود بانکی', 450000, 'INCOME', '1403/10/06', 'Income'),
    ('خرید دارو', 350000, 'EXPENSE', '1403/10/07', 'Health'),
    ('رستوران', 280000, 'EXPENSE', '1403/10/08', 'Food'),
    ('بنزین', 150000, 'EXPENSE', '1403/10/09', 'Transport'),
    ('خرید لباس', 2500000, 'EXPENSE', '1403/10/10', 'Shopping'),
    ('پاداش پروژه', 5000000, 'INCOME', '1403/10/15', 'Income'),
    ('قبض برق', 180000, 'EXPENSE', '1403/10/12', 'Housing'),
    ('سینما', 95000, 'EXPENSE', '1403/10/14', 'Other'),
]

# Clear old transactions
Transaction.objects.filter(user=admin).delete()

for title, amount, tx_type, date, cat_name in transactions_data:
    Transaction.objects.create(
        user=admin,
        title=title,
        amount=amount,
        type=tx_type,
        date=date,
        category=categories[cat_name]
    )

print(f"Created {len(transactions_data)} transactions")

# Create budgets
Budget.objects.filter(user=admin).delete()
budgets_data = [
    ('Food', 2000000),
    ('Transport', 500000),
    ('Shopping', 5000000),
    ('Health', 1000000),
]

for cat_name, limit in budgets_data:
    Budget.objects.create(
        user=admin,
        category=categories[cat_name],
        limit=limit,
        period='MONTHLY'
    )

print(f"Created {len(budgets_data)} budgets")

# Create goals
Goal.objects.filter(user=admin).delete()
goals_data = [
    ('خرید آیفون ۱۵', 50000000, 10000000, '1403/12/29'),
    ('سفر به ترکیه', 30000000, 5000000, '1404/03/15'),
    ('خرید لپ‌تاپ', 40000000, 15000000, '1404/06/01'),
]

for title, target, current, deadline in goals_data:
    Goal.objects.create(
        user=admin,
        title=title,
        target_amount=target,
        current_amount=current,
        deadline=deadline
    )

print(f"Created {len(goals_data)} goals")

print("\n✅ Test data created successfully!")
print("Login: admin / admin123")
print("URL: http://127.0.0.1:8000/")
