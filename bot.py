import json
import re
from playwright.sync_api import sync_playwright

def clean_price(price_str):
    if not price_str:
        return 0
    numbers = re.findall(r'\d+', str(price_str).replace(',', ''))
    return int("".join(numbers)) if numbers else 0

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
    elif any(k in t for k in ["حريمي", "نساء", "نسائي", "فستان", "عباية", "بلوزة", "طرحة", "women", "ladies", "شنطة حريمي"]):
        return "ملابس حريمي"
    elif any(k in t for k in ["رجالي", "رجال", "قميص", "بنطلون", "تيشيرت", "جاكيت", "بدلة", "men", "mens"]):
        return "ملابس رجالي"
    return "إلكترونيات"

def scrape_deals():
    all_deals = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        # ================= 1. أمازون مصر =================
        print("[1/6] جاري سحب صفقات أمازون مصر...")
        try:
            page.goto("https://www.amazon.eg/-/ar/gp/goldbox", timeout=45000)
            page.wait_for_timeout(3000)
            for _ in range(4):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(800)

            items = page.locator(".Grid-module_grid__C4G_L div.Grid-module_desktopGridItem__1_D6m").all()
            for item in items[:100]:
                try:
                    title_elem = item.locator(".Grid-module_gridItem__Title__1j2Kk").inner_text(timeout=300)
                    price_elem = item.locator(".a-price-whole").first.inner_text(timeout=300)
                    old_price_elem = item.locator(".a-text-price .a-offscreen").first.inner_text(timeout=300)
                    img_elem = item.locator("img").get_attribute("src", timeout=300)
                    link_elem = item.locator("a").get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        old_val = clean_price(old_price_elem) if old_price_elem else int(new_val * 1.3)
                        if new_val > 0:
                            disc_pct = int(round((1 - (new_val / old_val)) * 100)) if old_val > new_val else 20
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.amazon.eg{link_elem}"
                            full_url += ("&" if "?" in full_url else "?") + "tag=adelabed-21"

                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": f"{disc_pct}%",
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "أمازون مصر",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه أمازون: {e}")

        # ================= 2. نون مصر =================
        print("[2/6] جاري سحب صفقات نون مصر...")
        try:
            page.goto("https://www.noon.com/egypt-ar/deals/", timeout=45000)
            page.wait_for_timeout(3500)
            for _ in range(3):
                page.mouse.wheel(0, 2500)
                page.wait_for_timeout(800)

            noon_cards = page.locator("[data-qa^='product-box']").all()
            for card in noon_cards[:80]:
                try:
                    title_elem = card.locator("[qa-locator='product-name'], .sc-1a3b53b8-2, h2, h3").first.inner_text(timeout=300)
                    price_elem = card.locator("[qa-locator='product-price'], .amount").first.inner_text(timeout=300)
                    img_elem = card.locator("img").first.get_attribute("src", timeout=300)
                    link_elem = card.locator("a").first.get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        if new_val > 0:
                            old_val = int(new_val * 1.25)
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.noon.com{link_elem}"

                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": "20%",
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "نون مصر",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه نون: {e}")

        # ================= 3. جوميا مصر =================
        print("[3/6] جاري سحب صفقات جوميا مصر...")
        try:
            page.goto("https://www.jumia.com.eg/ar/flash-sales/", timeout=45000)
            page.wait_for_timeout(3500)
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(800)

            jumia_items = page.locator("article.prd._fb.col.c-shw, article.prd").all()
            for item in jumia_items[:80]:
                try:
                    title_elem = item.locator(".name").first.inner_text(timeout=300)
                    price_elem = item.locator(".prc").first.inner_text(timeout=300)
                    old_price_elem = item.locator(".old").first.inner_text(timeout=300)
                    img_elem = item.locator("img.img").first.get_attribute("data-src", timeout=300)
                    if not img_elem:
                        img_elem = item.locator("img.img").first.get_attribute("src", timeout=300)
                    link_elem = item.locator("a.core").first.get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        old_val = clean_price(old_price_elem) if old_price_elem else int(new_val * 1.3)
                        if new_val > 0:
                            disc_pct = int(round((1 - (new_val / old_val)) * 100)) if old_val > new_val else 25
                            full_url = link_elem if link_elem.startswith("http") else f"https://www.jumia.com.eg{link_elem}"

                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": f"{disc_pct}%",
                                "image": img_elem,
                                "productUrl": full_url,
                                "store": "جوميا مصر",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه جوميا: {e}")

        # ================= 4. بي تك =================
        print("[4/6] جاري سحب صفقات بي تك...")
        try:
            page.goto("https://btech.com/ar/hot-deals.html", timeout=45000)
            page.wait_for_timeout(3500)
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(800)

            btech_cards = page.locator(".product-item-info, .product-item").all()
            for card in btech_cards[:60]:
                try:
                    title_elem = card.locator(".product-item-link, .product-name").first.inner_text(timeout=300)
                    price_elem = card.locator(".price, [data-price-type='finalPrice']").first.inner_text(timeout=300)
                    img_elem = card.locator("img.product-image-photo").first.get_attribute("src", timeout=300)
                    link_elem = card.locator("a.product-item-link").first.get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        if new_val > 0:
                            old_val = int(new_val * 1.2)
                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": "16%",
                                "image": img_elem,
                                "productUrl": link_elem,
                                "store": "بي تك",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه بي تك: {e}")

        # ================= 5. رنين =================
        print("[5/6] جاري سحب صفقات رنين...")
        try:
            page.goto("https://raneen.com/ar/deals", timeout=45000)
            page.wait_for_timeout(3500)
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(800)

            raneen_cards = page.locator(".product-item-info, .product-item").all()
            for card in raneen_cards[:60]:
                try:
                    title_elem = card.locator(".product-item-link").first.inner_text(timeout=300)
                    price_elem = card.locator(".special-price .price, .price").first.inner_text(timeout=300)
                    img_elem = card.locator("img.product-image-photo").first.get_attribute("src", timeout=300)
                    link_elem = card.locator("a.product-item-link").first.get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        if new_val > 0:
                            old_val = int(new_val * 1.25)
                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": "20%",
                                "image": img_elem,
                                "productUrl": link_elem,
                                "store": "رنين",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه رنين: {e}")

        # ================= 6. 2B Egypt =================
        print("[6/6] جاري سحب صفقات 2B Egypt...")
        try:
            page.goto("https://2b.com.eg/ar/deals.html", timeout=45000)
            page.wait_for_timeout(3500)
            for _ in range(3):
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(800)

            tb_cards = page.locator(".product-item-info, .product-item").all()
            for card in tb_cards[:50]:
                try:
                    title_elem = card.locator(".product-item-link").first.inner_text(timeout=300)
                    price_elem = card.locator(".price").first.inner_text(timeout=300)
                    img_elem = card.locator("img.product-image-photo").first.get_attribute("src", timeout=300)
                    link_elem = card.locator("a.product-item-link").first.get_attribute("href", timeout=300)

                    if title_elem and price_elem:
                        new_val = clean_price(price_elem)
                        if new_val > 0:
                            old_val = int(new_val * 1.18)
                            all_deals.append({
                                "title": title_elem.strip(),
                                "newPrice": f"{new_val:,} ج.م",
                                "oldPrice": f"{old_val:,} ج.م",
                                "discount": "15%",
                                "image": img_elem,
                                "productUrl": link_elem,
                                "store": "2B",
                                "category": classify_category(title_elem)
                            })
                except Exception:
                    continue
        except Exception as e:
            print(f"[!] تنبيه 2B: {e}")

        browser.close()

    print(f"[*] تم سحب إجمالي {len(all_deals)} صفقة من 6 متاجر مصرية.")

    if len(all_deals) > 0:
        with open("deals.js", "w", encoding="utf-8") as f:
            f.write(f"const deals = {json.dumps(all_deals, ensure_ascii=False, indent=2)};")
        print(f"[✔] تم تحديث deals.js بنجاح!")

if __name__ == "__main__":
    scrape_deals()
