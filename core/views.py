from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.contrib import messages
from decimal import Decimal
import csv
import json
from datetime import datetime

try:
    import jdatetime
except ImportError:  # اگر jdatetime نصب نباشد، فیلتر ماه جاری غیرفعال می‌شود
    jdatetime = None

from .models import Transaction, Category, Budget, Goal, UserProfile
from .forms import UserRegisterForm, TransactionForm, BudgetForm, GoalForm, ProfileForm, CategoryForm
from .services.llama_service import get_financial_advice, analyze_spending, get_goal_advice


def get_or_create_default_categories():
    """Create default categories if they don't exist"""
    defaults = [
        ('Food', 'خوراکی', 'bi-cup-hot'),
        ('Transport', 'حمل و نقل', 'bi-car-front'),
        ('Shopping', 'خرید', 'bi-bag'),
        ('Housing', 'مسکن', 'bi-house'),
        ('Salary', 'حقوق', 'bi-briefcase'),
        ('Health', 'سلامت', 'bi-heart-pulse'),
        ('Income', 'درآمد', 'bi-wallet2'),
        ('Other', 'سایر', 'bi-three-dots'),
    ]
    
    for name, name_fa, icon in defaults:
        Category.objects.get_or_create(
            name=name, 
            is_default=True,
            defaults={'name_fa': name_fa, 'icon': icon}
        )
    
    return Category.objects.filter(is_default=True)


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    """Main dashboard view"""
    get_or_create_default_categories()
    
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate totals
    total_income = transactions.filter(type=Transaction.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type=Transaction.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    # Recent transactions
    recent_transactions = transactions[:5]
    
    # AI Analysis
    analysis = "در حال تحلیل..."
    if transactions.exists():
        tx_text = ', '.join([f"{t.title}: {t.amount}" for t in transactions[:5]])
        analysis = analyze_spending(tx_text)
    else:
        analysis = "هنوز تراکنشی ثبت نشده است."
    
    # Targeted Ad based on top spending category
    targeted_ad = None
    expenses = transactions.filter(type=Transaction.EXPENSE)
    if expenses.exists():
        category_totals = {}
        for t in expenses:
            cat_name = t.category.name if t.category else 'Other'
            category_totals[cat_name] = category_totals.get(cat_name, 0) + float(t.amount)
        
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            ads = {
                'Food': {'title': 'تخفیف ویژه سفارش غذا', 'desc': 'چون اهل دل هستی! ۳۰٪ تخفیف روی سفارش بعدی.', 'icon': '🍔', 'gradient': 'from-orange-400 to-red-500'},
                'Transport': {'title': 'بیمه بدنه خودرو', 'desc': 'هزینه‌های ماشینت زیاده؟ با بیمه خیال خودت رو راحت کن.', 'icon': '🚗', 'gradient': 'from-blue-400 to-indigo-600'},
                'Shopping': {'title': 'حراج فصل دیجی‌کالا', 'desc': 'لباس‌های جدید با ۵۰٪ تخفیف!', 'icon': '🛍️', 'gradient': 'from-pink-400 to-rose-600'},
                'Housing': {'title': 'وام تعمیرات مسکن', 'desc': 'با سود ۴٪ برای تعمیرات خانه وام بگیر.', 'icon': '🏠', 'gradient': 'from-emerald-400 to-teal-600'},
                'Health': {'title': 'بیمه تکمیلی سلامت', 'desc': 'هزینه‌های درمان بالاست. بیمه تکمیلی رو جدی بگیر.', 'icon': '💊', 'gradient': 'from-cyan-400 to-blue-500'},
            }
            targeted_ad = ads.get(top_category, {'title': 'سرمایه‌گذاری در بورس', 'desc': 'پول‌هات رو بیکار نذار!', 'icon': '📈', 'gradient': 'from-violet-400 to-purple-600'})
    
    # Chart data
    chart_data = []
    running_balance = 0
    for t in transactions.order_by('created_at'):
        if t.type == Transaction.INCOME:
            running_balance += float(t.amount)
        else:
            running_balance -= float(t.amount)
        chart_data.append(running_balance)
    
    context = {
        'balance': balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'recent_transactions': recent_transactions,
        'analysis': analysis,
        'targeted_ad': targeted_ad,
        'chart_data': json.dumps(chart_data[-10:] if chart_data else []),
        'categories': Category.objects.filter(Q(is_default=True) | Q(user=request.user)),
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def transactions(request):
    """Transactions list view"""
    transactions = Transaction.objects.filter(user=request.user)
    categories = Category.objects.filter(Q(is_default=True) | Q(user=request.user))
    
    context = {
        'transactions': transactions,
        'categories': categories,
    }
    return render(request, 'core/transactions.html', context)


@login_required
def add_transaction(request):
    """Add new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'تراکنش با موفقیت ثبت شد!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('dashboard')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    return redirect('dashboard')


@login_required
def export_transactions(request):
    """Export transactions as CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="kifpool-transactions.csv"'
    
    # Add BOM for Excel compatibility
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['id', 'title', 'amount', 'type', 'date', 'category'])
    
    transactions = Transaction.objects.filter(user=request.user)
    for t in transactions:
        writer.writerow([t.id, t.title, t.amount, t.type, t.date, t.category.name if t.category else 'Other'])
    
    return response


@login_required
def import_transactions(request):
    """Import transactions from CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            decoded_file = csv_file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded_file)

            valid_types = {Transaction.INCOME, Transaction.EXPENSE}
            count = 0
            skipped = 0
            for row in reader:
                # اعتبارسنجی هر سطر؛ سطر نامعتبر رد می‌شود تا کل واردات متوقف نشود.
                try:
                    amount = Decimal(str(row.get('amount', '')).strip())
                    if amount < 0:
                        raise ValueError('amount is negative')
                except (ValueError, ArithmeticError):
                    skipped += 1
                    continue

                tx_type = (row.get('type') or '').strip().upper()
                if tx_type not in valid_types:
                    tx_type = Transaction.EXPENSE

                category = Category.objects.filter(name=row.get('category', 'Other')).first()
                if not category:
                    category = Category.objects.filter(name='Other').first()

                Transaction.objects.create(
                    user=request.user,
                    title=(row.get('title') or 'Imported').strip(),
                    amount=amount,
                    type=tx_type,
                    date=(row.get('date') or '').strip(),
                    category=category
                )
                count += 1

            if skipped:
                messages.success(request, f'{count} تراکنش وارد شد. {skipped} سطر نامعتبر نادیده گرفته شد.')
            else:
                messages.success(request, f'{count} تراکنش با موفقیت وارد شد.')
        except Exception as e:
            messages.error(request, f'خطا در خواندن فایل: {str(e)}')
    
    return redirect('transactions')


@login_required
def analytics(request):
    """Analytics view with charts"""
    return render(request, 'core/analytics.html')


@login_required
def analytics_data(request):
    """API endpoint for chart data with period filtering"""
    period = request.GET.get('period', 'monthly')  # daily, weekly, monthly, yearly
    transactions = Transaction.objects.filter(user=request.user)
    
    # Group by period
    period_data = {}
    for t in transactions:
        if not t.date:
            key = 'Unknown'
        elif period == 'daily':
            key = t.date  # Full date
        elif period == 'weekly':
            # Group by week (first 7 chars + week indicator)
            key = t.date[:7] + '-W'  # Simplified week grouping
        elif period == 'yearly':
            key = t.date[:4] if len(t.date) >= 4 else 'Unknown'  # Just year
        else:  # monthly (default)
            key = t.date[:7] if len(t.date) >= 7 else 'Unknown'  # Year/Month
        
        if key not in period_data:
            period_data[key] = {'period': key, 'income': 0, 'expense': 0}
        
        if t.type == Transaction.INCOME:
            period_data[key]['income'] += float(t.amount)
        else:
            period_data[key]['expense'] += float(t.amount)
    
    # Category breakdown
    category_data = {}
    for t in transactions.filter(type=Transaction.EXPENSE):
        cat_name = t.category.name_fa if t.category else 'سایر'
        category_data[cat_name] = category_data.get(cat_name, 0) + float(t.amount)
    
    # Net worth over time
    net_worth_data = []
    cumulative = 0
    sorted_periods = sorted(period_data.keys())
    for p in sorted_periods:
        data = period_data[p]
        cumulative += data['income'] - data['expense']
        net_worth_data.append({'period': p, 'value': cumulative})
    
    # Calculate totals
    total_income = sum(d['income'] for d in period_data.values())
    total_expense = sum(d['expense'] for d in period_data.values())
    
    return JsonResponse({
        'period_data': list(period_data.values()),
        'categories': [{'name': k, 'value': v} for k, v in category_data.items()],
        'netWorth': net_worth_data,
        'totals': {
            'income': total_income,
            'expense': total_expense,
            'balance': total_income - total_expense
        }
    })


@login_required
def budget(request):
    """Budget tracker view"""
    categories = Category.objects.filter(Q(is_default=True) | Q(user=request.user))
    budgets = Budget.objects.filter(user=request.user)

    # محاسبه‌ی هزینه‌ی ماه جاری (شمسی). تاریخ‌ها با قالب «1403/MM/DD» ذخیره می‌شوند،
    # پس فقط تراکنش‌هایی که با پیشوند «سال/ماهِ» جاری شروع می‌شوند به حساب می‌آیند.
    transactions = Transaction.objects.filter(user=request.user, type=Transaction.EXPENSE)
    if jdatetime is not None:
        current_month = jdatetime.date.today().strftime('%Y/%m')  # مثل 1403/10
        transactions = transactions.filter(date__startswith=current_month)

    budget_data = []
    for category in categories:
        budget = budgets.filter(category=category).first()
        spent = transactions.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
        limit = budget.limit if budget else 0
        percent = int((spent / limit * 100)) if limit > 0 else 0
        
        budget_data.append({
            'category': category,
            'budget': budget,
            'spent': spent,
            'limit': limit,
            'percent': min(percent, 100),
            'over_budget': percent >= 100,
            'near_budget': 80 <= percent < 100,
        })
    
    context = {
        'budget_data': budget_data,
        'categories': categories,
    }
    return render(request, 'core/budget.html', context)


@login_required
def save_budget(request):
    """Save or update budget"""
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        limit = request.POST.get('limit')
        
        category = get_object_or_404(Category, id=category_id)
        
        budget, created = Budget.objects.update_or_create(
            user=request.user,
            category=category,
            defaults={'limit': Decimal(limit), 'period': Budget.MONTHLY}
        )
        
        messages.success(request, 'بودجه با موفقیت ذخیره شد!')
    
    return redirect('budget')


@login_required
def delete_budget(request, pk):
    """Delete budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    budget.delete()
    messages.success(request, 'بودجه حذف شد.')
    return redirect('budget')


@login_required
def goals(request):
    """Financial goals view"""
    goals = Goal.objects.filter(user=request.user)
    
    # Calculate total savings based on actual balance (Income - Expense)
    transactions = Transaction.objects.filter(user=request.user)
    total_income = transactions.filter(type=Transaction.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type=Transaction.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    total_saved = total_income - total_expense
    
    context = {
        'goals': goals,
        'total_saved': total_saved,
    }
    return render(request, 'core/goals.html', context)


@login_required
def add_goal(request):
    """Add new goal"""
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, 'هدف با موفقیت ایجاد شد!')
    
    return redirect('goals')


@login_required
def deposit_goal(request, pk):
    """Deposit to goal"""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            goal.current_amount += Decimal(amount)
            goal.save()
            messages.success(request, 'مبلغ با موفقیت اضافه شد!')
    
    return redirect('goals')


@login_required
def delete_goal(request, pk):
    """Delete goal"""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, 'هدف حذف شد.')
    return redirect('goals')


@login_required
def goal_advice(request, pk):
    """Get AI advice for goal"""
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    
    # Get spending context
    transactions = Transaction.objects.filter(user=request.user, type=Transaction.EXPENSE)[:10]
    spending_context = ', '.join([f"{t.amount} برای {t.category.name_fa if t.category else 'سایر'}" for t in transactions])
    
    advice = get_goal_advice(goal.title, float(goal.remaining), goal.deadline, spending_context)
    
    return JsonResponse({'advice': advice})


@login_required
def advisor(request):
    """Smart advisor view"""
    return render(request, 'core/advisor.html')


@login_required
def advisor_ask(request):
    """Ask AI advisor"""
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('query', '')
        
        # Build context from user's financial data
        transactions = Transaction.objects.filter(user=request.user)
        total_income = transactions.filter(type=Transaction.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = transactions.filter(type=Transaction.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
        
        context = f"""
        تعداد تراکنش‌ها: {transactions.count()}
        کل درآمد: {total_income:,} تومان
        کل هزینه: {total_expense:,} تومان
        موجودی: {(total_income - total_expense):,} تومان
        تراکنش‌های اخیر: {', '.join([f"{t.type} {t.amount} for {t.category.name if t.category else 'Other'}" for t in transactions[:10]])}
        """
        
        response = get_financial_advice(query, context)
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def profile(request):
    """Profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)


@login_required
def update_profile(request):
    """Update profile"""
    profile = request.user.userprofile
    
    if request.method == 'POST':
        # Update name
        first_name = request.POST.get('first_name', '')
        request.user.first_name = first_name
        request.user.save()
        
        # Update theme
        theme = request.POST.get('theme', 'olive')
        profile.theme = theme
        
        # Update avatar
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'پروفایل با موفقیت بروزرسانی شد!')
    
    return redirect('profile')


@login_required
def categories(request):
    """Categories management view"""
    user_categories = Category.objects.filter(user=request.user)
    default_categories = Category.objects.filter(is_default=True)
    
    context = {
        'user_categories': user_categories,
        'default_categories': default_categories,
    }
    return render(request, 'core/categories.html', context)


@login_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.user, request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.name = category.name_fa  # Use Persian name as internal name too
            category.save()
            messages.success(request, 'دسته‌بندی با موفقیت ایجاد شد!')
            return redirect('categories')
    else:
        form = CategoryForm(request.user)
    
    return render(request, 'core/category_form.html', {'form': form, 'title': 'افزودن دسته‌بندی'})


@login_required
def edit_category(request, pk):
    """Edit category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.user, request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.name = category.name_fa
            category.save()
            messages.success(request, 'دسته‌بندی ویرایش شد.')
            return redirect('categories')
    else:
        form = CategoryForm(request.user, instance=category)
    
    return render(request, 'core/category_form.html', {'form': form, 'title': 'ویرایش دسته‌بندی'})


@login_required
def delete_category(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    category.delete()
    messages.success(request, 'دسته‌بندی حذف شد.')
    return redirect('categories')
