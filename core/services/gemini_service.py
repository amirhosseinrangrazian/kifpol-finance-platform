"""
Gemini AI Service for KifPool
"""
import requests
import json
from django.conf import settings


def call_gemini_api(prompt):
    """Call Gemini API with the given prompt"""
    url = f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        # print(f"Calling Gemini API: {settings.GEMINI_API_URL}")
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        # print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            # print(f"Error response: {response.text}")
            return f"خطا در ارتباط با API (کد {response.status_code})"
        
        result = response.json()
        
        # Extract text from response
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
        
        # print(f"Unexpected response format: {result}")
        return "متاسفانه نتوانستم پاسخی تولید کنم."
        
    except requests.exceptions.Timeout:
        # print("Gemini API Timeout")
        return "زمان انتظار برای پاسخ به پایان رسید. لطفا مجددا تلاش کنید."
    except requests.exceptions.RequestException as e:
        # print(f"Gemini API Error: {e}")
        return "خطا در ارتباط با هوش مصنوعی. لطفا مجددا تلاش کنید."
    except Exception as e:
        # print(f"Unexpected error: {e}")
        return f"خطای غیرمنتظره: {str(e)}"


import datetime

def get_financial_advice(query, context):
    """Get financial advice from Gemini"""
    today = datetime.date.today().strftime("%Y/%m/%d")
    prompt = f"""شما یک مشاور مالی حرفه‌ای هستید. با توجه به اطلاعات زیر به سوال کاربر پاسخ دهید.

تاریخ امروز: {today} (میلادی)
توجه: کاربر از تقویم شمسی استفاده می‌کند.

اطلاعات مالی کاربر:
{context}

سوال کاربر: {query}

لطفا پاسخ خود را به زبان فارسی و به صورت حرفه‌ای اما دوستانه بنویسید. راهکارهای عملی و قابل اجرا ارائه دهید."""
    
    return call_gemini_api(prompt)


def analyze_spending(transactions_text):
    """Analyze spending patterns"""
    today = datetime.date.today().strftime("%Y/%m/%d")
    prompt = f"""تاریخ امروز: {today} (میلادی)

این تراکنش‌های مالی را تحلیل کن و یک خلاصه ۲-۳ جمله‌ای از الگوی مخارج به فارسی بنویس. لحن رسمی و دلگرم‌کننده باشد:

{transactions_text}"""
    
    return call_gemini_api(prompt)


def get_goal_advice(goal_title, amount_needed, deadline, spending_context):
    """Get advice for achieving a financial goal"""
    today = datetime.date.today().strftime("%Y/%m/%d")
    prompt = f"""تاریخ امروز: {today} (میلادی)
می‌خواهم {amount_needed:,} تومان برای "{goal_title}" تا تاریخ {deadline} (شمسی) پس‌انداز کنم.

وضعیت هزینه‌های اخیر من: {spending_context}

لطفا ۳ پیشنهاد کوتاه و عملی به فارسی برای رسیدن به این هدف بر اساس عادات خرج کردن من بده. پاسخ را به صورت لیست بنویس.
همچنین محاسبه کن چقدر زمان دارم و آیا با روند فعلی رسیدن به هدف ممکن است یا خیر."""
    
    return call_gemini_api(prompt)
