import json
import os
from flask import Flask, render_template_string, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from io import BytesIO
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
JSON_FILE = "urun.json"
PRICE_HISTORY_FILE = "fiyat_gecmisi.json"

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Sepetim Stok Kontrol</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #fff;
            color: #222;
            margin: 10px 15px 20px 15px;
            font-size: 14px;
        }

        h2 {
            text-align: center;
            margin-bottom: 15px;
            font-size: 20px;
        }

        .container {
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
            flex-wrap: nowrap; /* 4 sütun yan yana */
            gap: 10px;
        }

        .column {
            width: 24%;
            box-sizing: border-box;
            padding: 5px;
        }

        .product {
            position: relative;
            border: 1px solid #ccc;
            padding: 8px;
            margin: 8px 0;
            text-align: center;
            border-radius: 5px;
            background-color: #fafafa;
            transition: box-shadow 0.3s ease;
            font-size: 13px;
        }

        .product:hover {
            box-shadow: 0 3px 7px rgba(0,0,0,0.1);
        }

        .delete-btn {
            position: absolute;
            top: 4px;
            right: 4px;
            border: none;
            background: transparent;
            cursor: pointer;
            font-size: 16px;
            color: #d9534f;
            transition: color 0.2s ease;
        }

        .delete-btn:hover {
            color: #c9302c;
        }

        img {
            max-width: 18%;
            height: auto;
            border-radius: 4px;
            margin-bottom: 6px;
        }

        h3 {
            text-align: center;
            background-color: #f0f0f0;
            padding: 8px;
            margin-top: 0;
            border-radius: 5px 5px 0 0;
            font-size: 16px;
        }

        form {
            margin-bottom: 15px;
            text-align: center;
        }

        input[type="text"] {
            padding: 6px 10px;
            font-size: 14px;
            border-radius: 4px;
            border: 1px solid #ccc;
            width: 350px;
            transition: border-color 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #5bc0de;
            outline: none;
        }

        button {
            background-color: #5bc0de;
            color: white;
            border: none;
            padding: 7px 14px;
            font-size: 14px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #31b0d5;
        }

        details summary {
            cursor: pointer;
            font-weight: 600;
            margin-top: 8px;
            font-size: 13px;
        }

        details ul {
            margin-top: 4px;
            padding-left: 18px;
            max-height: 80px;
            overflow-y: auto;
            color: #555;
            font-size: 12px;
        }

        a {
            color: #5bc0de;
            text-decoration: none;
            font-weight: 600;
            font-size: 13px;
        }

        a:hover {
            text-decoration: underline;
        }

        #sepetTutari {
            font-weight: bold;
            font-size: 17px;
            color: #27ae60;
        }

        /* Mobilde 4 sütun alt alta %100 genişlik */
        @media (max-width: 900px) {
            .container {
                flex-wrap: wrap;
            }
            .column {
                width: 100% !important;
                margin-bottom: 15px;
            }
            input[type="text"] {
                width: 90%;
            }
        }
    </style>
</head>
<body>
    <h2>Alışveriş Sepetim Stok Kontrol</h2>
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
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <a href="/export_excel"><button type="button">Excel Olarak İndir</button></a>
    <div style="font-weight: bold; font-size: 18px;">
         🛒 Sepet Tutarı: <span id="sepetTutari">
            {{ "{:,.2f}".format(toplam_fiyat).replace(",", "X").replace(".", ",").replace("X", ".") }} TL
        </span>
    </div>
</div>


    <div class="container">
        <div class="column">
            <h3>✔️ Stokta Olan Ürünler</h3>
            {% for product in stokta %}
                <div class="product">
                    <button class="delete-btn" onclick="deleteProduct('{{ product.url }}')">🗑️</button>
                    <img src="{{ product.image }}" alt="Resim Yok">
                    <p><strong>{{ product.name }}</strong></p>
                    <p>{{ product.price }}</p>
                    <details>
                        <summary>📈 Fiyat Geçmişi</summary>
                        <ul>
                        {% for entry in product.history %}
                            <li>{{ entry.date }} — {{ entry.price }}</li>
                        {% endfor %}
                        </ul>
                    </details>
                    <p><strong>Renk:</strong> {{ product.color }}</p>
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
                    <details>
                        <summary>📈 Fiyat Geçmişi</summary>
                        <ul>
                        {% for entry in product.history %}
                            <li>{{ entry.date }} — {{ entry.price }}</li>
                        {% endfor %}
                        </ul>
                    </details>
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
                    <p><strong>Renk:</strong> {{ product.color }}</p>
                    <p><small>Güncellenme: {{ product.last_updated }}</small></p>
                    <a href="{{ product.url }}" target="_blank">Link</a>
                </div>
            {% else %}
                <p>Yeni stoğa giren ürün bulunmamaktadır.</p>
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
                    <p><small>Güncellenme: {{ product.last_updated }}</small></p>
                    <a href="{{ product.url }}" target="_blank">Link</a>
                </div>
            {% else %}
                <p>Yeni stoğu tükenen ürün bulunmamaktadır.</p>
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

def load_price_history():
    if not os.path.exists(PRICE_HISTORY_FILE):
        return {}
    try:
        with open(PRICE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_price_history(data):
    with open(PRICE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def update_price_history(product):
    url = product["url"]
    price = product["price"]
    today_str = datetime.now().strftime("%Y-%m-%d")

    if price == "Bilinmiyor":
        print(f"Fiyat bilinmiyor, fiyat geçmişi güncellenmedi: {url}")
        return

    history_data = load_price_history()
    product_history = history_data.get(url, [])

    if not any(entry["date"] == today_str and entry["price"] == price for entry in product_history):
        product_history.append({"date": today_str, "price": price})
        history_data[url] = product_history
        save_price_history(history_data)
        print(f"Fiyat geçmişi güncellendi: {url} - {price} - {today_str}")
    else:
        print(f"Aynı fiyat zaten kayıtlı: {url} - {price} - {today_str}")



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
    for category in ["stokta", "stokta_degil"]:
        data[category] = [p for p in data[category] if p["url"] != product["url"]]
    update_price_history(product)
    if product["status"] == "stokta":
        data["stokta"].append(product)
    elif product["status"] == "stokta_degil":
        data["stokta_degil"].append(product)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/price_history')
def price_history():
    history = load_price_history()
    return jsonify(history)

def parse_price(price_str):
    try:
     return float(price_str.replace(" TL", "").replace(".", "").replace(",", "."))
    except:
      return{}
    




def check_stock_zara(url):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        try:
            product_name_element = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '#main > div > div.product-detail-view-std > div.product-detail-view__main-content > div.product-detail-view__main-info > div > div.product-detail-info__info > div.product-detail-info__header > div > h1'
            )))
            product_name = product_name_element.text.strip()
        except Exception:
            product_name = "Bilinmiyor"

        try:
            product_price_element = driver.find_element(By.CSS_SELECTOR,
                '#main > div > div > div.product-detail-view__main-content > div.product-detail-view__main-info > div > div.product-detail-info__info > div.product-detail-info__price > div > span > ins > span > div > span')
            product_price = product_price_element.text.strip()
        except NoSuchElementException:
            try:
                product_price_element = driver.find_element(By.CSS_SELECTOR,
                    '#main > div > div > div.product-detail-view__main-content > div.product-detail-view__main-info > div > div.product-detail-info__info > div.product-detail-info__price > div > span > span > span > div > span')
                product_price = product_price_element.text.strip()
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
            product_color_element = driver.find_element(
                By.CSS_SELECTOR,
                '#main > div > div > div.product-detail-view__main-content > div.product-detail-view__main-info > div > p'
            )
            product_color = product_color_element.text.strip()
        except NoSuchElementException:
            product_color = "Bilinmiyor"

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
            "color": product_color
        }
    except Exception as e:
        return {"status": f"hata: {e}"}
    finally:
        driver.quit()

def attach_history(product, history_data):
    product['history'] = history_data.get(product['url'], [])
    return product

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
                "image": data.get("image", ""),
                "color": data.get("color", "Bilinmiyor")
            }
            save_product(product)
            product_info = product

            if product["status"] == "stokta":
                result = "✅ Ürün stokta ve kaydedildi."
            else:
                result = "❌ Ürün stokta değil ve kaydedildi."

    all_data = load_saved_products()
    history_data = load_price_history()

    for category in ["stokta", "stokta_degil", "yeni_stokta", "yeni_stokta_degil"]:
        all_data[category] = [attach_history(p, history_data) for p in all_data.get(category, [])]

    def filter_products(products):
        if not search:
            return products
        return [p for p in products if search in p["name"].lower()]

    stokta_filtered = filter_products(all_data.get("stokta", []))
    stokta_degil_filtered = filter_products(all_data.get("stokta_degil", []))

    toplam_fiyat=sum(parse_price(p["price"]) for p in stokta_filtered if "price" in p )

    return render_template_string(
        HTML_TEMPLATE,
        result=result,
        url=url,
        stokta=stokta_filtered,
        stokta_degil=stokta_degil_filtered,
        yeni_stokta=all_data.get("yeni_stokta", []),
        yeni_stokta_degil=all_data.get("yeni_stokta_degil", []),
        product_info=product_info,
        search=search,
        toplam_fiyat=toplam_fiyat
    )

def send_email(subject, body, attachment_path=None):
    sender_email = os.environ.get("EMAIL_SENDER")
    sender_password = os.environ.get("EMAIL_PASSWORD")
    receiver_email = os.environ.get("EMAIL_RECEIVER")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("✅ E-posta gönderildi.")
    except Exception as e:
        print(f"❌ E-posta gönderilemedi: {e}")

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
                    "status": new_status,
                    "color": new_data.get("color", product.get("color", "Bilinmiyor")),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                save_product(updated_product)

                if new_status == "stokta" and prev_status == "stokta_degil":
                    yeni_stokta.append(updated_product)
                    print(f"🆕 Yeni stok: {updated_product['name']}")
                    send_email(
                        subject=f"Stok Güncellemesi: '{updated_product['name']}' Stokta!",
                        body=f"Ürün '{updated_product['name']}' stok durumunu değiştirdi ve şimdi stokta.\nLink: {updated_product['url']}"
                    )
                elif new_status == "stokta_degil" and prev_status == "stokta":
                    yeni_stokta_degil.append(updated_product)
                    print(f"📉 Stok tükendi: {updated_product['name']}")
                    send_email(
                        subject=f"Stok Güncellemesi: '{updated_product['name']}' Stoğu Tükendi!",
                        body=f"Ürün '{updated_product['name']}' stok durumunu değiştirdi ve artık stokta değil.\nLink: {updated_product['url']}"
                    )

    current_data = load_saved_products()
    current_data["yeni_stokta"] = yeni_stokta
    current_data["yeni_stokta_degil"] = yeni_stokta_degil

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=4, ensure_ascii=False)

    if not yeni_stokta and not yeni_stokta_degil:
        print("✅ Stok güncellemesi yok.")
        send_email(
            subject="Stok Güncellemesi: Değişiklik Yok",
            body="Şu anda hiçbir üründe stok durumu değişikliği bulunmamaktadır.",
        )

    return current_data

@app.route('/delete_product', methods=['POST'])
def delete_product():
    url_to_delete = request.json.get("url")
    if not url_to_delete:
        return jsonify({"success": False, "error": "URL verilmedi"}), 400

    data = load_saved_products()
    original_stokta_len = len(data["stokta"])
    original_stokta_degil_len = len(data["stokta_degil"])

    data["stokta"] = [p for p in data["stokta"] if p["url"] != url_to_delete]
    data["stokta_degil"] = [p for p in data["stokta_degil"] if p["url"] != url_to_delete]

    if len(data["stokta"]) < original_stokta_len or len(data["stokta_degil"]) < original_stokta_degil_len:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Ürün bulunamadı"}), 404

@app.route('/export_excel')
def export_excel():
    all_data = load_saved_products()
    combined = all_data.get("stokta", []) + all_data.get("stokta_degil", [])

    if not combined:
        df = pd.DataFrame(columns=["name", "price", "status"])
    else:
        df = pd.DataFrame(combined)
        df = df[["name", "price", "status"]]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Products')
    output.seek(0)

    return send_file(
        output,
        download_name="products.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    if os.environ.get("GITHUB_ACTIONS") == "true":
        check_all_products_periodically()
    else:
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_all_products_periodically, 'interval', minutes=10)
        scheduler.start()

        app.run(debug=True, use_reloader=False)
