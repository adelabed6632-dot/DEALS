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
    
    if discount_percent < 5 or discount_percent > 85:
        return False, f"{discount_percent}%", new_p, old_p
        
    return True, f"{discount_percent}%", new_p, old_p

def scrape_deals():
    deals = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        print("[*] جاري سحب أحدث الصفقات الحقيقية وتصنيف الأقسام الجديدة...")

        try:
            page.goto("https://www.amazon.eg/-/ar/gp/goldbox?ref_=nav_cs_gb", timeout=60000)
            page.wait_for_timeout(5000)

            items = page.locator(".Grid-module_grid__C4G_L div.Grid-module_desktopGridItem__1_D6m").all()
            
            for item in items[:45]:
                try:
                    title_elem = item.locator(".Grid-module_gridItem__Title__1j2Kk").inner_text(timeout=1000)
                    price_elem = item.locator(".a-price-whole").first.inner_text(timeout=1000)
                    old_price_elem = item.locator(".a-text-price .a-offscreen").first.inner_text(timeout=1000)
                    img_elem = item.locator("img").get_attribute("src", timeout=1000)
                    link_elem = item.locator("a").get_attribute("href", timeout=1000)

                    if title_elem and price_elem:
                        new_p_str = f"{price_elem} ج.م"
                        old_p_str = f"{old_price_elem} ج.م" if old_price_elem else f"{int(clean_price(price_elem) * 1.25)} ج.م"
                        
                        is_valid, disc_str, new_val, old_val = validate_deal(new_p_str, old_p_str)
                        
                        if is_valid:
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.amazon.eg{link_elem}"
                            if "?" in full_url:
                                full_url += "&tag=adelabed-21"
                            else:
                                full_url += "?tag=adelabed-21"

                            # نظام التصنيف التلقائي المحدث (يشمل السوبرماركت والملابس بنوعيها)
                            category = "إلكترونيات"
                            t_lower = title_elem.lower()
                            
                            if any(k in t_lower for k in ["سمن", "زيت", "أرز", "مكرونة", "شاي", "بن", "سكر", "حليب", "جبنة", "بيض", "مسحوق", "سوبرماركت", "طعام", "تغليف"]):
                                category = "سوبرماركت"
                            elif any(k in t_lower for k in ["موبايل", "هاتف", "phone", "iphone", "samsung", "xiaomi"]):
                                category = "هواتف"
                            elif any(k in t_lower for k in ["تلفزيون", "شاشة", "tv", "screen"]):
                                category = "شاشات"
                            elif any(k in t_lower for k in ["ثلاجة", "غسالة", "مكواة", "خلاط", "بوتاجاز", "ميكروويف"]):
                                category = "أجهزة كهربائية"
                            elif any(k in t_lower for k in ["حذاء", "جزمة", "شوز", "shoes", "سنيكرز"]):
                                category = "أحذية"
                            elif any(k in t_lower for k in ["حريمي", "نساء", "نسائي", "فستان", "عباية", "بلوزة", "جيبة", "women", "ladies", "girl"]):
                                category = "ملابس حريمي"
                            elif any(k in t_lower for k in ["رجالي", "رجال", "رجالي", "قميص رجالي", "بنطلون رجالي", "men", "mens", "boy"]):
                                category = "ملابس رجالي"

                            deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": disc_str,
                                "discount_val": disc_str,
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "أمازون مصر",
                                "category": category
                            })
                except Exception:
                    continue

        except Exception as e:
            print(f"[!] تنبيه أثناء السحب: {e}")

        browser.close()

    js_content = f"const deals = {json.dumps(deals, ensure_ascii=False, indent=2)};"
    with open("deals.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"[✔] تم سحب وتصنيف {len(deals)} عرضاً وتحديث الأقسام بنجاح!")

if __name__ == "__main__":
    scrape_deals()
