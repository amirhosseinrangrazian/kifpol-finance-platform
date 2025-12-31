from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    """دسته‌بندی تراکنش‌ها"""
    name = models.CharField(max_length=100, verbose_name='نام')
    name_fa = models.CharField(max_length=100, verbose_name='نام فارسی', blank=True)
    icon = models.CharField(max_length=50, default='bi-tag', verbose_name='آیکون')
    color = models.CharField(max_length=7, default='#3f4f28', verbose_name='رنگ')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories', verbose_name='دسته والد')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='کاربر')
    is_default = models.BooleanField(default=False, verbose_name='پیش‌فرض')

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name_fa or self.parent.name} » {self.name_fa or self.name}"
        return self.name_fa or self.name


class Transaction(models.Model):
    """تراکنش مالی"""
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'
    TYPE_CHOICES = [
        (INCOME, 'درآمد'),
        (EXPENSE, 'هزینه'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='مبلغ')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='نوع')
    date = models.CharField(max_length=10, verbose_name='تاریخ')  # Format: 1403/MM/DD
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='دسته‌بندی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Budget(models.Model):
    """سقف بودجه برای هر دسته‌بندی"""
    MONTHLY = 'MONTHLY'
    WEEKLY = 'WEEKLY'
    PERIOD_CHOICES = [
        (MONTHLY, 'ماهانه'),
        (WEEKLY, 'هفتگی'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='دسته‌بندی')
    limit = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='سقف بودجه')
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default=MONTHLY, verbose_name='دوره')

    class Meta:
        verbose_name = 'بودجه'
        verbose_name_plural = 'بودجه‌ها'
        unique_together = ['user', 'category']

    def __str__(self):
        return f"{self.category} - {self.limit}"


class Goal(models.Model):
    """اهداف مالی"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    title = models.CharField(max_length=200, verbose_name='عنوان')
    target_amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='مبلغ هدف')
    current_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='مبلغ فعلی')
    deadline = models.CharField(max_length=10, verbose_name='مهلت')  # Format: 1403/MM/DD
    icon = models.CharField(max_length=50, default='bi-trophy', verbose_name='آیکون')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'هدف مالی'
        verbose_name_plural = 'اهداف مالی'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def progress(self):
        if self.target_amount > 0:
            return min(int((self.current_amount / self.target_amount) * 100), 100)
        return 0

    @property
    def remaining(self):
        return max(self.target_amount - self.current_amount, 0)


class UserProfile(models.Model):
    """پروفایل کاربر"""
    THEME_CHOICES = [
        ('olive', 'زیتونی'),
        ('blu', 'آبی'),
        ('berry', 'تمشکی'),
        ('dark', 'تیره'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='کاربر')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='olive', verbose_name='تم')

    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
