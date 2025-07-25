import json
import os
from flask import Flask, render_template_string, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from io import BytesIO
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


from flask import Flask, render_template, request, send_file
from io import BytesIO

app = Flask(__name__)
JSON_FILE = "urun.json"

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Zara Stok Kontrol</title>
    <style>
        .container {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }
        .column {
            width: 45%;
        }
        .product {
            position: relative; /* Silme butonu için gerekli */
            border: 1px solid #ccc;
            padding: 10px;
            margin: 10px 0;
            text-align: center;
        }
        .delete-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 18px;
            color: red;
        }
        img {
            max-width: 15%;
            height: auto;
        }
        h3 {
            text-align: center;
            background-color: #f0f0f0;
            padding: 10px;
        }
    </style>
</head>
<body>
    <h2>Zara Stok Kontrol</h2>
    <form method="POST">
        <label>Ürün URL'si:</label>
        <input type="text" name="url" style="width:400px;" required>
        <button type="submit">Kontrol Et</button>
    </form>

    {% if url %}
        <p><strong>Girilen URL:</strong> {{ url }}</p>
    {% endif %}
    <form method="GET" style="margin-bottom:20px;">
        <input type="text" name="search" placeholder="Ürün adına göre ara" value="{{ search | default('') }}">
        <button type="submit">Ara</button>
    </form>
    <div style="margin-bottom: 20px;">
        <a href="/export_excel"><button type="button">Excel Olarak İndir</button></a>
    </div>

    {% if result %}
        <p><strong>Sonuç:</strong> {{ result }}</p>
    {% endif %}

   <div class="container">
    <div class="column">
        <h3>✔️ Stokta Olan Ürünler</h3>
        {% for product in stokta %}
            <div class="product">
                <button class="delete-btn" onclick="deleteProduct('{{ product.url }}')">🗑️</button>
                <img src="{{ product.image }}" alt="Resim Yok">
                <p><strong>{{ product.name }}</strong></p>
                <p>{{ product.price }}</p>
               
                <a href="{{ product.url }}" target="_blank">Link</a>
            </div>
        {% endfor %}
    </div>

    <div class="column">
        <h3>❌ Stokta Olmayan Ürünler</h3>
        {% for product in stokta_degil %}
            <div class="product">
                <button class="delete-btn" onclick="deleteProduct('{{ product.url }}')">🗑️</button>
                <img src="{{ product.image }}" alt="Resim Yok">
                <p><strong>{{ product.name }}</strong></p>
                <p>{{ product.price }}</p>
               
                <a href="{{ product.url }}" target="_blank">Link</a>
            </div>
        {% endfor %}
    </div>

    <div class="column">
        <h3>🆕 Yeni Stoğa Giren Ürünler</h3>
        {% for product in yeni_stokta %}
            <div class="product">
                <button class="delete-btn" onclick="deleteProduct('{{ product.url }}')">🗑️</button>
                <img src="{{ product.image }}" alt="Resim Yok">
                <p><strong>{{ product.name }}</strong></p>
                <p>{{ product.price }}</p>
               
                <a href="{{ product.url }}" target="_blank">Link</a>
            </div>
        {% endfor %}
    </div>

    <div class="column">
        <h3>📉 Yeni Stoğu Tükenen Ürünler</h3>
        {% for product in yeni_stokta_degil %}
            <div class="product">
                <button class="delete-btn" onclick="deleteProduct('{{ product.url }}')">🗑️</button>
                <img src="{{ product.image }}" alt="Resim Yok">
                <p><strong>{{ product.name }}</strong></p>
                <p>{{ product.price }}</p>
              
                <a href="{{ product.url }}" target="_blank">Link</a>
            </div>
        {% endfor %}
    </div>
</div>


<script>
function deleteProduct(url) {
    if(confirm("Bu ürünü silmek istediğinize emin misiniz?")) {
        fetch('/delete_product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
                // CSRF varsa ekle: 'X-CSRFToken': '...' 
            },
            body: JSON.stringify({ url: url })
        }).then(response => {
            if(response.ok) {
                alert("Ürün silindi.");
                location.reload();
            } else {
                alert("Silme işlemi başarısız.");
            }
        });
    }
}
</script>
</body>
</html>
"""

def load_saved_products():
    if not os.path.exists(JSON_FILE):
        return {"stokta": [], "stokta_degil": [], "yeni_stokta": [], "yeni_stokta_degil": []}
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("yeni_stokta", [])
            data.setdefault("yeni_stokta_degil", [])
            return data
    except Exception:
        return {"stokta": [], "stokta_degil": [], "yeni_stokta": [], "yeni_stokta_degil": []}


def save_product(product):
    data = load_saved_products()

    data["stokta"] = [p for p in data["stokta"] if p["url"] != product["url"]]
    data["stokta_degil"] = [p for p in data["stokta_degil"] if p["url"] != product["url"]]

   

    
    if product["status"] == "stokta":
        data["stokta"].append(product)
    elif product["status"] == "stokta_degil":
        data["stokta_degil"].append(product)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def check_stock_zara(url):
    

    options = Options()
    
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # WebDriver otomatik yüklensin:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  


    try:
        driver.get(url)

        try:
            product_name = driver.find_element(
                By.CSS_SELECTOR,
                '#main > div > div.product-detail-view-std > div.product-detail-view__main-content > div.product-detail-view__main-info > div > div.product-detail-info__info > div.product-detail-info__header > div > h1'
            ).text.strip()
        except NoSuchElementException:
            product_name = "Bilinmiyor"

        try:
            product_price = driver.find_element(
                By.CSS_SELECTOR,'#main > div > div.product-detail-view-std > div.product-detail-view__main-content > div.product-detail-view__main-info > div > div.product-detail-info__info > div.product-detail-info__price > div > span > span > span > div > span'
            ).text.strip()
        except NoSuchElementException:
            product_price = "Bilinmiyor"

        try:
            product_img = driver.find_element(
                By.CSS_SELECTOR,
                '#main > div > div > div.product-detail-view__main-content > div.product-detail-view__main-image-wrapper > button > div > div > picture > img'
            ).get_attribute('src')
        except NoSuchElementException:
            product_img = ""

        try:
            add_button = driver.find_element(By.CSS_SELECTOR, 'button[data-qa-action="add-to-cart"]')
            button_text = add_button.text.strip()

            if "EKLE" in button_text:
                status = "stokta"
            elif "BENZER ÜRÜNLER" in button_text:
                status = "stokta_degil"
            else:
                status = "belirsiz"
        except NoSuchElementException:
            status = "stokta_degil"

        return {
            "status": status,
            "name": product_name,
            "price": product_price,
            "image": product_img,
        }

    except Exception as e:
        return {"status": f"hata: {e}"}

    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    url = None
    search = request.args.get('search', '').lower()
    product_info = None

    if request.method == 'POST':
        url = request.form.get('url').strip()
        data = check_stock_zara(url)

        if "hata:" in data.get("status", ""):
            result = f"⚠️ Hata oluştu: {data['status']}"
        elif data.get("status") == "belirsiz":
            result = "⚠️ Ürün durumu belirlenemedi."
        else:
            product = {
                "url": url,
                "status": data["status"],
                "name": data.get("name", "Bilinmiyor"),
                "price": data.get("price", "Bilinmiyor"),
                "image": data.get("image", "")
            }
            save_product(product)
            product_info = product

            if product["status"] == "stokta":
                result = "✅ Ürün stokta ve kaydedildi."
            else:
                result = "❌ Ürün stokta değil ve kaydedildi."

    all_data = load_saved_products()

    # Aramaya göre filtreleme yap
    def filter_products(products):
        if not search:
            return products
        return [p for p in products if search in p["name"].lower()]

    stokta_filtered = filter_products(all_data.get("stokta", []))
    stokta_degil_filtered = filter_products(all_data.get("stokta_degil", []))

   

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        url=url,
        stokta=stokta_filtered,
        stokta_degil=stokta_degil_filtered,
        product_info=product_info,
         yeni_stokta=load_saved_products().get("yeni_stokta", []),
        yeni_stokta_degil=load_saved_products().get("yeni_stokta_degil", []),
        search=search
    )
@app.route('/export_excel')
def export_excel():
    all_data = load_saved_products()
    combined = all_data.get("stokta", []) + all_data.get("stokta_degil", [])

    if not combined:
        df = pd.DataFrame(columns=["status", "name", "price", "url", "image"])
    else:
        df = pd.DataFrame(combined)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Products')
    output.seek(0)

    return send_file(output,
                     download_name="products.xlsx",
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    url_to_delete = request.json.get("url")
    if not url_to_delete:
        return jsonify({"success": False, "error": "URL verilmedi"}), 400

    data = load_saved_products()
    original_stokta_len = len(data["stokta"])
    original_stokta_degil_len = len(data["stokta_degil"])

    # URL'ye göre filtreleme (silme)
    data["stokta"] = [p for p in data["stokta"] if p["url"] != url_to_delete]
    data["stokta_degil"] = [p for p in data["stokta_degil"] if p["url"] != url_to_delete]

    if len(data["stokta"]) < original_stokta_len or len(data["stokta_degil"]) < original_stokta_degil_len:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Ürün bulunamadı"}), 404



def check_all_products_periodically():
    data = load_saved_products()
    yeni_stokta = []
    yeni_stokta_degil = []

    for category in ["stokta", "stokta_degil"]:
        for product in data[category]:
            url = product["url"]
            print(f"{url} için stok kontrolü yapılıyor...")
            new_data = check_stock_zara(url)

            if "hata:" in new_data.get("status", "") or new_data.get("status") == "belirsiz":
                print(f"{url} durumu belirsiz, atlandı.")
                continue

            prev_status = product.get("status")
            new_status = new_data["status"]

            if new_status != prev_status:
                updated_product = {
                    "url": url,
                    "name": new_data.get("name", product["name"]),
                    "price": new_data.get("price", product["price"]),
                    "image": new_data.get("image", product["image"]),
                    "status": new_status
                }
                save_product(updated_product)

                if new_status == "stokta" and prev_status == "stokta_degil":
                    yeni_stokta.append(updated_product)
                elif new_status == "stokta_degil" and prev_status == "stokta":
                    yeni_stokta_degil.append(updated_product)
    with open(JSON_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["yeni_stokta"] = yeni_stokta
        data["yeni_stokta_degil"] = yeni_stokta_degil
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()
   



    
    

if __name__ == '__main__':
    if os.environ.get("GITHUB_ACTIONS") == "true":
        check_all_products_periodically()
    else:
        app.run(debug=True)