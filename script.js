const container = document.getElementById("deals");

// دالة تقرأ أحدث العروض التي جهزها الروبوت
async function fetchDeals() {
  try {
    const res = await fetch("deals.json");
    const items = await res.json();

    container.innerHTML = ""; // مسح القديم وعرض الجديد
    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <img src="${item.image}" alt="">
        <h3>${item.title}</h3>
        <div class="prices"><span class="price">${item.price}</span></div>
        <a href="${item.link}" target="_blank" class="btn">شراء الآن</a>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.log("في انتظار بدء الروبوت وتجهيز الملف...");
  }
}

// قراءة العروض فور فتح الصفحة
fetchDeals();

// تفقد وجود عروض جديدة كل دقيقة بدون الحاجة لعمل تحديث يدوي للصفحة
setInterval(fetchDeals, 60000);