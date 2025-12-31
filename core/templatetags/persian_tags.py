from django import template

register = template.Library()


@register.filter
def persian_number(value):
    """Convert English numbers to Persian"""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    
    result = str(value)
    for en, fa in zip(english_digits, persian_digits):
        result = result.replace(en, fa)
    return result


@register.filter
def format_amount(value):
    """Format amount with Persian numbers and comma separators"""
    try:
        formatted = '{:,}'.format(int(value))
        return persian_number(formatted)
    except (ValueError, TypeError):
        return value


@register.filter
def category_icon(category_name):
    """Get Bootstrap icon class for category"""
    icons = {
        'Food': 'bi-cup-hot',
        'Transport': 'bi-car-front',
        'Shopping': 'bi-bag',
        'Housing': 'bi-house',
        'Salary': 'bi-briefcase',
        'Health': 'bi-heart-pulse',
        'Income': 'bi-wallet2',
        'Other': 'bi-three-dots',
    }
    return icons.get(category_name, 'bi-tag')


@register.filter
def category_name_fa(category_name):
    """Get Persian name for category"""
    names = {
        'Food': 'خوراکی',
        'Transport': 'حمل و نقل',
        'Shopping': 'خرید',
        'Housing': 'مسکن',
        'Salary': 'حقوق',
        'Health': 'سلامت',
        'Income': 'درآمد',
        'Other': 'سایر',
    }
    return names.get(category_name, category_name)
