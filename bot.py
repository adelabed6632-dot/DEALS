import json
import re
from playwright.sync_api import sync_playwright

def clean_price(price_str):
    if not price_str:
        return 0
    numbers = re.findall(r'\d+', price_str.replace(',', ''))
    return int("".join(numbers)) if numbers else 0

def validate_deal(new_price_str, old_price_str):
    new_p = clean_price(new_price_str)
    old_p = clean_price(old_price_str)
    
    if old_p <= new_p or new_p == 0:
        return False, "0%", new_p, old_p
    
    discount_percent = int(round((1 - (new_p / old_p)) * 100))
    
    if discount_percent < 3 or discount_percent > 90:
        return False, f"{discount_percent}%", new_p, old_p
        
    return True, f"{discount_percent}%", new_p, old_p

def classify_category(title_elem):
    t_lower = title_elem.lower()
    if any(k in t_lower for k in ["سمن", "زيت", "أرز", "مكرونة", "شاي", "بن", "سكر", "حليب", "جبنة", "بيض", "مسحوق", "منظف", "شيبس", "شوكولاتة", "سوبرماركت", "قهوة", "نسكافيه", "طعام", "تغليف"]):
        return "سوبرماركت"
    elif any(k in t_lower for k in ["موبايل", "هاتف", "phone", "iphone", "samsung", "xiaomi", "redmi", "oppo", "infinix"]):
        return "هواتف"
    elif any(k in t_lower for k in ["تلفزيون", "شاشة", "tv", "screen", "سمارت"]):
        return "شاشات"
    elif any(k in t_lower for k in ["ثلاجة", "غسالة", "مكواة", "خلاط", "بوتاجاز", "ميكروويف", "كاتل", "دفاية", "تكييف"]):
        return "أجهزة كهربائية"
    elif any(k in t_lower for k in ["حذاء", "جزمة", "شوز", "shoes", "سنيكرز", "صندل", "شبشب", "كوتشي"]):
        return "أحذية"
    elif any(k in t_lower for k in ["حريمي", "نساء", "نسائي", "فستان", "عباية", "بلوزة", "جيبة", "women", "ladies", "girl", "حجاب", "طرحة"]):
        return "ملابس حريمي"
    elif any(k in t_lower for k in ["رجالي", "رجال", "قميص", "بنطلون", "تيشيرت", "جاكيت", "men", "mens", "boy", "بولاور"]):
        return "ملابس رجالي"
    return "إلكترونيات"

def scrape_deals():
    deals = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # ================= 1. سحب عروض أمازون مصر =================
        print("[*] جاري سحب عروض أمازون مصر...")
        try:
            page.goto("https://www.amazon.eg/-/ar/gp/goldbox?ref_=nav_cs_gb", timeout=60000)
            page.wait_for_timeout(4000)
            for _ in range(5):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)

            items = page.locator(".Grid-module_grid__C4G_L div.Grid-module_desktopGridItem__1_D6m").all()
            for item in items[:250]:
                try:
                    title_elem = item.locator(".Grid-module_gridItem__Title__1j2Kk").inner_text(timeout=500)
                    price_elem = item.locator(".a-price-whole").first.inner_text(timeout=500)
                    old_price_elem = item.locator(".a-text-price .a-offscreen").first.inner_text(timeout=500)
                    img_elem = item.locator("img").get_attribute("src", timeout=500)
                    link_elem = item.locator("a").get_attribute("href", timeout=500)

                    if title_elem and price_elem:
                        new_p_str = f"{price_elem} ج.م"
                        old_p_str = f"{old_price_elem} ج.م" if old_price_elem else f"{int(clean_price(price_elem) * 1.3)} ج.م"
                        is_valid, disc_str, new_val, old_val = validate_deal(new_p_str, old_p_str)
                        
                        if is_valid:
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.amazon.eg{link_elem}"
                            full_url += ("&" if "?" in full_url else "?") + "tag=adelabed-21"

                            deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": disc_str,
                                "discount_val": disc_str,
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "أمازون مصر",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] خطأ في أمازون: {e}")

        # ================= 2. سحب عروض نون مصر =================
        print("[*] جاري سحب عروض نون مصر (Noon Egypt)...")
        try:
            page.goto("https://www.noon.com/egypt-ar/deals/", timeout=60000)
            page.wait_for_timeout(4000)
            for _ in range(4):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)

            noon_items = page.locator("[data-qa^='product-box']").all()
            for item in noon_items[:200]:
                try:
                    title_elem = item.locator(".sc-1a3b53b8-2, [qa-locator='product-name']").inner_text(timeout=500)
                    price_elem = item.locator(".amount, [qa-locator='product-price']").first.inner_text(timeout=500)
                    img_elem = item.locator("img").get_attribute("src", timeout=500)
                    link_elem = item.locator("a").get_attribute("href", timeout=500)

                    if title_elem and price_elem:
                        new_p_str = f"{price_elem} ج.م"
                        old_p_str = f"{int(clean_price(price_elem) * 1.25)} ج.م" # سعر تقديري افتراضي للخصم في نون
                        is_valid, disc_str, new_val, old_val = validate_deal(new_p_str, old_p_str)
                        
                        if is_valid:
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.noon.com{link_elem}"
                            # يمكنك إضافة كود أفلييت نون لاحقاً هنا إن وجد

                            deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": "20%",
                                "discount_val": "20%",
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "نون مصر",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] خطأ في نون: {e}")

        browser.close()

    # حفظ النتائج في ملف deals.js
    js_content = f"const deals = {json.dumps(deals, ensure_ascii=False, indent=2)};"
    with open("deals.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"[✔] تم بنجاح سحب إجمالي {len(deals)} صفقة من مختلف المتاجر المصرية وتحديث الملف!")

if __name__ == "__main__":
    scrape_deals()
