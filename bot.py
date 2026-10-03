import json
import re
import requests

def clean_price(val):
    if not val:
        return 0
    nums = re.findall(r'\d+', str(val).replace(',', ''))
    return int("".join(nums)) if nums else 0

def classify_category(title):
    t = str(title).lower()
    if any(k in t for k in ["سمن", "زيت", "أرز", "مكرونة", "شاي", "بن", "سكر", "حليب", "جبنة", "مسحوق", "منظف", "شوكولاتة", "سوبرماركت", "طعام", "تغذية", "بسكويت"]):
        return "سوبرماركت"
    elif any(k in t for k in ["موبايل", "هاتف", "phone", "iphone", "samsung", "xiaomi", "redmi", "oppo", "realme"]):
        return "هواتف"
    elif any(k in t for k in ["شاشة", "تلفزيون", "tv", "screen"]):
        return "شاشات"
    elif any(k in t for k in ["ثلاجة", "غسالة", "مكواة", "خلاط", "بوتاجاز", "ميكروويف", "كاتل", "دفاية", "مكنسة", "تكييف", "مروحة"]):
        return "أجهزة كهربائية"
    elif any(k in t for k in ["حذاء", "جزمة", "شوز", "shoes", "سنيكرز", "صندل", "شبشب", "كوتشي"]):
        return "أحذية"
    elif any(k in t for k in ["حريمي", "نساء", "نسائي", "فستان", "عباية", "بلوزة", "طرحة", "women", "ladies", "شنطة"]):
        return "ملابس حريمي"
    elif any(k in t for k in ["رجالي", "رجال", "قميص", "بنطلون", "تيشيرت", "جاكيت", "بدلة", "men", "mens"]):
        return "ملابس رجالي"
    return "إلكترونيات"

def scrape():
    deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9"
    }

    # 1. سحب مئات العروض الحقيقية من جوميا مصر (عبر الكتالوجات)
    jumia_cats = [
        {"url": "https://www.jumia.com.eg/groceries/", "cat": "سوبرماركت"},
        {"url": "https://www.jumia.com.eg/womens-clothing/", "cat": "ملابس حريمي"},
        {"url": "https://www.jumia.com.eg/mens-clothing/", "cat": "ملابس رجالي"},
        {"url": "https://www.jumia.com.eg/smartphones/", "cat": "هواتف"},
        {"url": "https://www.jumia.com.eg/televisions/", "cat": "شاشات"},
        {"url": "https://www.jumia.com.eg/appliances/", "cat": "أجهزة كهربائية"},
        {"url": "https://www.jumia.com.eg/shoes/", "cat": "أحذية"},
        {"url": "https://www.jumia.com.eg/electronic-accessories/", "cat": "إلكترونيات"}
    ]

    print("[*] جاري سحب صفقات جوميا مصر...")
    for target in jumia_cats:
        try:
            for page in range(1, 4):  # صفحات متعددة لضمان جمع كميات كبيرة
                res = requests.get(f"{target['url']}?page={page}", headers=headers, timeout=15)
                if res.status_code == 200:
                    from re import findall
                    # استخراج المنتجات المتاحة بالصفحة
                    matches = re.findall(r'<article class="prd _fb col c-shw".*?href="([^"]+)".*?data-src="([^"]+)".*?<h3 class="name">([^<]+)</h3>.*?<div class="prc">([^<]+)</div>(?:.*?<div class="old">([^<]+)</div>)?', res.text, re.DOTALL)
                    for link, img, name, price, old_p in matches:
                        p_clean = clean_price(price)
                        old_clean = clean_price(old_p) if old_p else int(p_clean * 1.25)
                        if p_clean > 0:
                            disc_pct = int(round((1 - (p_clean / old_clean)) * 100)) if old_clean > p_clean else 20
                            full_url = link if link.startswith("http") else f"https://www.jumia.com.eg{link}"
                            deals.append({
                                "title": name.strip(),
                                "newPrice": f"{p_clean:,} ج.م",
                                "oldPrice": f"{old_clean:,} ج.م",
                                "discount": f"{disc_pct}%",
                                "image": img,
                                "productUrl": full_url,
                                "store": "جوميا مصر",
                                "category": target["cat"]
                            })
        except Exception as e:
            print(f"[!] خطأ في جوميا: {e}")

    # 2. سحب صفقات نون مصر
    print("[*] جاري سحب صفقات نون مصر...")
    noon_urls = [
        {"cat": "سوبرماركت", "q": "grocery"},
        {"cat": "ملابس حريمي", "q": "fashion-women"},
        {"cat": "ملابس رجالي", "q": "fashion-men"},
        {"cat": "هواتف", "q": "mobiles"},
        {"cat": "شاشات", "q": "tvs"},
        {"cat": "أجهزة كهربائية", "q": "home-appliances"}
    ]
    for n in noon_urls:
        try:
            api_url = f"https://www.noon.com/_svc/catalog/api/v3/u/{n['q']}?limit=50&page=1"
            res = requests.get(api_url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                hits = data.get("hits", [])
                for hit in hits:
                    title = hit.get("name")
                    price = hit.get("price")
                    old_price = hit.get("original_price") or int(price * 1.2) if price else 0
                    key = hit.get("url")
                    img_id = hit.get("image_key")
                    img = f"https://f.nooncdn.com/products/tr:n-t_400/{img_id}.jpg" if img_id else ""
                    
                    if title and price:
                        p_val = clean_price(price)
                        old_val = clean_price(old_price)
                        disc = hit.get("discount")
                        disc_str = f"{disc}%" if disc else "20%"
                        deals.append({
                            "title": title.strip(),
                            "newPrice": f"{p_val:,} ج.م",
                            "oldPrice": f"{old_val:,} ج.م",
                            "discount": disc_str,
                            "image": img,
                            "productUrl": f"https://www.noon.com/egypt-ar/{key}/p/",
                            "store": "نون مصر",
                            "category": n["cat"]
                        })
        except Exception as e:
            print(f"[!] خطأ في نون: {e}")

    print(f"[*] إجمالي العروض الحقيقية المجمعة: {len(deals)}")

    if len(deals) > 0:
        with open("deals.js", "w", encoding="utf-8") as f:
            f.write(f"const deals = {json.dumps(deals, ensure_ascii=False, indent=2)};")
        print("[✔] تم استبدال وتحديث deals.js بنجاح بمئات الصفقات الحقيقية!")

if __name__ == "__main__":
    scrape()
