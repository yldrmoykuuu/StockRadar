
📦 Stok Takip ve Bildirim Uygulaması
Bu proje, belirli e-ticaret sitelerindeki ürünlerin stok ve fiyat durumlarını otomatik olarak takip eden, değişikliklerde kullanıcıya e-posta ile bildirim gönderen bir web uygulamasıdır.
Ürün bilgileri Selenium ile çekilir, JSON dosyasında saklanır ve HTML sayfada renkli uyarılarla kullanıcıya sunulur.
Proje ayrıca ürün arama, filtreleme, fiyat değişim takibi ve dışa aktarma özelliklerine sahiptir.

⚙️ Kullanılan Teknolojiler
🐍 Python: Uygulama kodları için.

🌐 Selenium: Web otomasyonu ve ürün bilgilerini çekmek için.

📁 JSON: Ürün verilerinin saklanması için.

🔄 GitHub Actions: Otomatik zamanlanmış stok kontrolü için.

📧 SMTP (Python smtplib): E-posta bildirimleri göndermek için.

📊 Matplotlib veya Plotly (isteğe bağlı): Fiyat değişim grafikleri için.

📊 Pandas: Excel/CSV dışa aktarma işlemleri için.

🚀 Ana Özellikler
🟢🔴 Renkli uyarılar: Ürün stok durumuna göre yeşil (stokta), kırmızı (stokta yok).

🏷️ Ürün detayları: Ürün adı, fiyat, resim ve URL bilgilerini çekme ve kaydetme.

✨ Yeni Stoğa Gelenler: HTML sayfada “Yeni Stoğa Gelenler” bölümünde yeni ürünleri listeleme.

🔍 Arama ve filtreleme: URL, ürün adı ve stok durumu bazında hızlı arama ve filtreleme.

📥 Excel/CSV dışa aktarma: Kayıtlı ürün listesini kolayca dışa aktarma.

📈 Fiyat değişim takibi: Fiyat değişikliklerini takip edip grafiklerle gösterme.

🗑️ Silme butonu: İstenmeyen ürünleri listeden kaldırma.

⏲️ Arka planda stok kontrolü: Belirli aralıklarla otomatik stok takibi ve mail bildirimleri.

📄 JSON veri takibi: Ürün durumu ve stok değişikliklerinin detaylı kaydı.
