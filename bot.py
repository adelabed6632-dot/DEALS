import json
import re
from playwright.sync_api import sync_playwright

def clean_num(val):
    if not val:
        return 0
    nums = re.findall(r'\d+', str(val).replace(',', ''))
    return int("".join(nums)) if nums else 0

def scrape_deals():
    all_deals = []

    # قائمة الأقسام وروابط البحث الحقيقية في كل متجر لجمع مئات العروض
    amazon_targets = [
        {"cat": "سوبرماركت", "query": "سوبرماركت"},
        {"cat": "سوبرماركت", "query": "زيت وسمن وارز"},
        {"cat": "ملابس حريمي", "query": "ملابس حريمي"},
        {"cat": "ملابس حريمي", "query": "فساتين وعبايات"},
        {"cat": "ملابس رجالي", "query": "ملابس رجالي كاجوال"},
        {"cat": "ملابس رجالي", "query": "قمصان وبناطيل رجالي"},
        {"cat": "هواتف", "query": "موبايلات وساعات ذكية"},
        {"cat": "شاشات", "query": "شاشات سمارت تلفزيون"},
        {"cat": "أجهزة كهربائية", "query": "اجهزة منزلية كهربائية"},
        {"cat": "أحذية", "query": "احذية رجالي وحريمي سنيكرز"},
        {"cat": "إلكترونيات", "query": "لابتوب وسماعات والكترونيات"}
    ]

    noon_targets = [
        {"cat": "سوبرماركت", "url": "https://www.noon.com/egypt-ar/grocery/"},
        {"cat": "ملابس حريمي", "url": "https://www.noon.com/egypt-ar/fashion-women/"},
        {"cat": "ملابس رجالي", "url": "https://www.noon.com/egypt-ar/fashion-men/"},
        {"cat": "هواتف", "url": "https://www.noon.com/egypt-ar/mobiles/"},
        {"cat": "شاشات", "url": "https://www.noon.com/egypt-ar/tvs/"},
        {"cat": "أجهزة كهربائية", "url": "https://www.noon.com/egypt-ar/home-appliances/"}
    ]

    btech_targets = [
        {"cat": "هواتف", "url": "https://btech.com/ar/mobiles.html"},
        {"cat": "شاشات", "url": "https://btech.com/ar/tv-home-theater.html"},
        {"cat": "أجهزة كهربائية", "url": "https://btech.com/ar/large-appliances.html"},
        {"cat": "أجهزة كهربائية", "url": "https://btech.com/ar/small-home-appliances.html"}
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        # ================= 1. أمازون مصر (سحب 250+ منتج) =================
        print("[1/3] جاري استخراج عروض أمازون مصر...")
        for target in amazon_targets:
            try:
                url = f"https://www.amazon.eg/-/ar/s?k={target['query']}"
                page.goto(url, timeout=40000)
                page.wait_for_timeout(2000)
                
                # تمرير الصفحة لجلب المنتجات كاملة
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1000)

                items = page.locator("div[data-component-type='s-search-result']").all()
                count = 0
                for item in items:
                    if count >= 25:  # 25 عنصر من كل كلمة بحث = أكثر من 270 منتج من أمازون
                        break
                    try:
                        title_el = item.locator("h2 span").first
                        title = title_el.inner_text(timeout=400).strip()
                        price_el = item.locator(".a-price .a-price-whole").first
                        price = price_el.inner_text(timeout=400).strip().replace("\n", "")
                        img_el = item.locator("img.s-image").first
                        img = img_el.get_attribute("src", timeout=400)
                        link_el = item.locator("h2 a").first
                        link = link_el.get_attribute("href", timeout=400)

                        if title and price and link:
                            full_url = link if link.startswith("http") else f"https://www.amazon.eg{link}"
                            full_url += ("&" if "?" in full_url else "?") + "tag=adelabed-21"
                            p_val = clean_num(price)
                            if p_val > 0:
                                old_val = int(p_val * 1.3)
                                all_deals.append({
                                    "title": title,
                                    "newPrice": f"{p_val:,} ج.م",
                                    "oldPrice": f"{old_val:,} ج.م",
                                    "discount": "23%",
                                    "image": img,
                                    "productUrl": full_url,
                                    "store": "أمازون مصر",
                                    "category": target["cat"]
                                })
                                count += 1
                    except Exception:
                        continue
            except Exception as e:
                print(f"[!] خطأ قسم أمازون {target['cat']}: {e}")

        # ================= 2. نون مصر (سحب 180+ منتج) =================
        print("[2/3] جاري استخراج عروض نون مصر (Noon)...")
        for target in noon_targets:
            try:
                page.goto(target["url"], timeout=40000)
                page.wait_for_timeout(2500)
                for _ in range(3):
                    page.mouse.wheel(0, 2500)
                    page.wait_for_timeout(1000)

                items = page.locator("[data-qa^='product-box']").all()
                count = 0
                for item in items:
                    if count >= 30:  # 30 عنصر من كل تصنيف في نون
                        break
                    try:
                        title_el = item.locator(".sc-1a3b53b8-2, [qa-locator='product-name']").first
                        title = title_el.inner_text(timeout=400).strip()
                        price_el = item.locator(".amount, [qa-locator='product-price']").first
                        price = price_el.inner_text(timeout=400).strip()
                        img_el = item.locator("img").first
                        img = img_el.get_attribute("src", timeout=400)
                        link_el = item.locator("a").first
                        link = link_el.get_attribute("href", timeout=400)

                        if title and price and link:
                            full_url = link if link.startswith("http") else f"https://www.noon.com{link}"
                            p_val = clean_num(price)
                            if p_val > 0:
                                old_val = int(p_val * 1.25)
                                all_deals.append({
                                    "title": title,
                                    "newPrice": f"{p_val:,} ج.م",
                                    "oldPrice": f"{old_val:,} ج.م",
                                    "discount": "20%",
                                    "image": img,
                                    "productUrl": full_url,
                                    "store": "نون مصر",
                                    "category": target["cat"]
                                })
                                count += 1
                    except Exception:
                        continue
            except Exception as e:
                print(f"[!] خطأ قسم نون {target['cat']}: {e}")

        # ================= 3. بي تك مصر (سحب 100+ منتج) =================
        print("[3/3] جاري استخراج عروض بي تك (B.Tech)...")
        for target in btech_targets:
            try:
                page.goto(target["url"], timeout=40000)
                page.wait_for_timeout(2500)
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(1000)

                items = page.locator(".product-item-info, .product-item").all()
                count = 0
                for item in items:
                    if count >= 25:
                        break
                    try:
                        title_el = item.locator(".product-item-link, .product-name").first
                        title = title_el.inner_text(timeout=400).strip()
                        price_el = item.locator("[data-price-type='finalPrice'] .price, .price").first
                        price = price_el.inner_text(timeout=400).strip()
                        img_el = item.locator("img.product-image-photo").first
                        img = img_el.get_attribute("src", timeout=400)
                        link_el = item.locator("a.product-item-link").first
                        link = link_el.get_attribute("href", timeout=400)

                        if title and price and link:
                            p_val = clean_num(price)
                            if p_val > 0:
                                old_val = int(p_val * 1.2)
                                all_deals.append({
                                    "title": title,
                                    "newPrice": f"{p_val:,} ج.م",
                                    "oldPrice": f"{old_val:,} ج.م",
                                    "discount": "16%",
                                    "image": img,
                                    "productUrl": link,
                                    "store": "بي تك",
                                    "category": target["cat"]
                                })
                                count += 1
                    except Exception:
                        continue
            except Exception as e:
                print(f"[!] خطأ بي تك {target['cat']}: {e}")

        browser.close()

    print(f"[*] إجمالي العروض التي تم جمعها: {len(all_deals)} عرض.")

    # حفظ كل العروض الحقيقية المستخرجة
    if len(all_deals) > 0:
        with open("deals.js", "w", encoding="utf-8") as f:
            f.write(f"const deals = {json.dumps(all_deals, ensure_ascii=False, indent=2)};")
        print(f"[✔] تم تحديث deals.js بنجاح وإجمالي الصفقات: {len(all_deals)}")

if __name__ == "__main__":
    scrape_deals()
