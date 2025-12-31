"""
Llama AI Service for KifPool
Local model running on localhost:8080
"""
import requests
import json
import datetime
from django.conf import settings


def call_llama_api(prompt):
    """Call local Llama API with the given prompt"""
    url = settings.LLAMA_API_URL
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.LLAMA_API_SECRET}',
    }
    
    # OpenAI-compatible format for llama.cpp server
    data = {
        "messages": [
            {
                "role": "system",
                "content": "تو یک دستیار مالی فارسی هستی. کوتاه و ساده جواب بده."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        
        if response.status_code != 200:
            return f"خطا در ارتباط با مدل (کد {response.status_code})"
        
        result = response.json()
        
        # Extract text from OpenAI-compatible response
        if 'choices' in result and len(result['choices']) > 0:
            choice = result['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
        
        return "متاسفانه نتوانستم پاسخی تولید کنم."
        
    except requests.exceptions.Timeout:
        return "زمان انتظار برای پاسخ به پایان رسید. لطفا مجددا تلاش کنید."
    except requests.exceptions.RequestException as e:
        return "خطا در ارتباط با هوش مصنوعی. لطفا مجددا تلاش کنید."
    except Exception as e:
        return f"خطای غیرمنتظره: {str(e)}"


def get_financial_advice(query, context):
    """Get financial advice from Llama - simplified prompt"""
    today = datetime.date.today().strftime("%Y/%m/%d")
    
    # Simplified prompt for less capable model
    prompt = f"""اطلاعات مالی:
{context}

سوال: {query}

یک پاسخ کوتاه و مفید به فارسی بده."""
    
    return call_llama_api(prompt)


def analyze_spending(transactions_text):
    """Analyze spending patterns - simplified prompt"""
    
    # Simplified prompt
    prompt = f"""این تراکنش‌ها را ببین:
{transactions_text}

یک خلاصه ۲ جمله‌ای از وضعیت مخارج به فارسی بنویس."""
    
    return call_llama_api(prompt)


def get_goal_advice(goal_title, amount_needed, deadline, spending_context):
    """Get advice for achieving a financial goal - simplified prompt"""
    
    # Simplified prompt
    prompt = f"""هدف: {goal_title}
مبلغ: {amount_needed:,} تومان
مهلت: {deadline}

۳ پیشنهاد ساده برای پس‌انداز بده به فارسی."""
    
    return call_llama_api(prompt)
