import json
from playwright.sync_api import sync_playwright

def scrape_deals():
    deals = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.amazon.eg/-/ar/gp/goldbox", timeout=45000)
            page.wait_for_timeout(3000)

            items = page.locator(".Grid-module_grid__C4G_L div.Grid-module_desktopGridItem__1_D6m").all()
            for item in items[:40]:
                try:
                    title = item.locator(".Grid-module_gridItem__Title__1j2Kk").inner_text(timeout=500)
                    price = item.locator(".a-price-whole").first.inner_text(timeout=500)
                    img = item.locator("img").get_attribute("src", timeout=500)
                    link = item.locator("a").get_attribute("href", timeout=500)

                    if title and price:
                        full_url = link if link.startswith("http") else f"https://www.amazon.eg{link}"
                        if "?" in full_url:
                            full_url += "&tag=adelabed-21"
                        else:
                            full_url += "?tag=adelabed-21"

                        # تحديد القسم
                        cat = "إلكترونيات"
                        t_low = title.lower()
                        if any(k in t_low for k in ["سمن", "زيت", "سكر", "شاي", "سوبرماركت"]):
                            cat = "سوبرماركت"
                        elif any(k in t_low for k in ["حريمي", "نساء", "فستان", "عباية"]):
                            cat = "ملابس حريمي"
                        elif any(k in t_low for k in ["رجالي", "قميص", "بنطلون"]):
                            cat = "ملابس رجالي"
                        elif any(k in t_low for k in ["موبايل", "هاتف", "phone"]):
                            cat = "هواتف"

                        deals.append({
                            "title": title.strip(),
                            "newPrice": f"{price} ج.م",
                            "oldPrice": f"{int(int(price.replace(',', '')) * 1.3)} ج.م",
                            "discount": "25%",
                            "image": img,
                            "productUrl": full_url,
                            "store": "أمازون مصر",
                            "category": cat
                        })
                except:
                    continue
            browser.close()
    except Exception as e:
        print(f"Error: {e}")

    # حماية أكيدة: لو البوت ملقاش صفقات لأي سبب، يحفظ المنتجات الأساسية بدل ما يصفر الملف
    if not deals:
        deals = [
            {
                "title": "عرض السلع والزيوت الأساسية - سوبرماركت أمازون",
                "newPrice": "149 ج.م", "oldPrice": "220 ج.م", "discount": "32%",
                "image": "https://m.media-amazon.com/images/I/61lzVbyZgZL._AC_SX679_.jpg",
                "productUrl": "https://www.amazon.eg/-/ar/gp/goldbox?tag=adelabed-21",
                "store": "أمازون مصر", "category": "سوبرماركت"
            }
        ]

    with open("deals.js", "w", encoding="utf-8") as f:
        f.write(f"const deals = {json.dumps(deals, ensure_ascii=False, indent=2)};")

if __name__ == "__main__":
    scrape_deals()
