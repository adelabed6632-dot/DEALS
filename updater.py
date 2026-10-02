import json
import time
import schedule
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ضع هنا كود الأفلييت الخاص بك ليضاف لأي رابط تلقائياً
AFFILIATE_TAG = "?tag=mydeals-21"

def fetch_latest_deals():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] جاري فحص وجلب أحدث الخصومات...")
    
    deals = []

    # إعداد ترويسة المتصفح حتى لا يتم حظر السكريبت
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
    }

    # مثال على جلب عروض وتخفيضات (يمكن إضافة روابط أقسام العروض التي تختارها)
    # هنا نجهز الهيكل البرمجي لمعالجة البيانات:
    sample_scraped_items = [
        {
            "id": 1,
            "title": "سماعة بلوتوث لاسلكية عازلة للضوضاء",
            "store": "أمازون",
            "category": "electronics",
            "oldPrice": 1200,
            "currentPrice": 750,
            "discount": "38%",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
            "rawUrl": "https://www.amazon.eg/dp/B08XJG8B5C"
        },
        {
            "id": 2,
            "title": "ماكينة إعداد قهوة اسبريسو احترافية",
            "store": "نون",
            "category": "home",
            "oldPrice": 3400,
            "currentPrice": 2199,
            "discount": "35%",
            "image": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500&q=80",
            "rawUrl": "https://www.noon.com/egypt-ar/coffee-machine"
        },
        {
            "id": 3,
            "title": "ساعة ذكية رياضية مقاومة للماء مع حساس نبض",
            "store": "أمازون",
            "category": "electronics",
            "oldPrice": 950,
            "currentPrice": 499,
            "discount": "47%",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
            "rawUrl": "https://www.amazon.eg/dp/B09Y88B44X"
        }
    ]

    # إضافة رابط التسويق بالعمولة (Affiliate Link) لكل منتج وحفظه
    for item in sample_scraped_items:
        clean_url = item["rawUrl"].split("?")[0]
        item["affiliateUrl"] = f"{clean_url}{AFFILIATE_TAG}"
        deals.append(item)

    # حفظ النتائج داخل ملف deals.json ليقرأه الموقع فوراً
    with open("deals.json", "w", encoding="utf-8") as f:
        json.dump(deals, f, ensure_ascii=False, indent=2)

    print(f"تم بنجاح تحديث {len(deals)} عرض، وتم الحفظ في deals.json.")

# تشغيل التحديث فور بدء البرنامج
fetch_latest_deals()

# جدولة الكود ليعمل تلقائياً كل 30 دقيقة
schedule.every(30).minutes.do(fetch_latest_deals)

print("المُحدِّث التلقائي يعمل الآن... يكرر الفحص كل 30 دقيقة. اضغط Ctrl+C للإيقاف.")
while True:
    schedule.run_pending()
    time.sleep(1)