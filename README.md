
📦Zara Stok Takip ve Bildirim Uygulaması


Bu proje, belirli e-ticaret sitelerindeki ürünlerin stok ve fiyat durumlarını otomatik olarak takip eden, değişikliklerde kullanıcıya e-posta ile bildirim gönderen bir web uygulamasıdır.
Ürün bilgileri Selenium ile çekilir, JSON dosyasında saklanır ve HTML sayfada renkli uyarılarla kullanıcıya sunulur.
Proje ayrıca ürün arama, filtreleme, fiyat değişim takibi ve dışa aktarma özelliklerine sahiptir.

⚙️ Kullanılan Teknolojiler
 Python: Uygulama kodları için.

Selenium: Web otomasyonu ve ürün bilgilerini çekmek için.

 JSON: Ürün verilerinin saklanması için.

 GitHub Actions: Otomatik zamanlanmış stok kontrolü için.

SMTP (Python smtplib): E-posta bildirimleri göndermek için.

Matplotlib veya Plotly (isteğe bağlı): Fiyat değişim grafikleri için.

 Pandas: Excel/CSV dışa aktarma işlemleri için.

🚀 Ana Özellikler
 Renkli uyarılar: Ürün stok durumuna göre yeşil (stokta), kırmızı (stokta yok).

 Ürün detayları: Ürün adı, fiyat, resim ve URL bilgilerini çekme ve kaydetme.
 
<img width="431" height="663" alt="image" src="https://github.com/user-attachments/assets/108d1cf4-783f-4bb3-a50d-af4496304dfb" />


 Yeni Stoğa Gelenler: HTML sayfada “Yeni Stoğa Gelenler” bölümünde yeni ürünleri listeleme.
<img width="1892" height="980" alt="yeni_stoğu_tükenenlerin_stokta_yok" src="https://github.com/user-attachments/assets/f32a21da-aec3-4b9b-a9a3-105a9e328dfe" />
 Arama ve filtreleme: URL, ürün adı ve stok durumu bazında hızlı arama ve filtreleme.
<img width="1900" height="917" alt="filtreleme" src="https://github.com/user-attachments/assets/d4d659fe-a872-4771-9a22-d4cfa1e5326d" />

 Excel/CSV dışa aktarma: Kayıtlı ürün listesini kolayca dışa aktarma.

<img width="715" height="561" alt="excel_product" src="https://github.com/user-attachments/assets/f3fef6f9-86fa-42d1-9319-0470a447c3e1" />

 Fiyat değişim takibi: Fiyat değişikliklerini takip edip gösterme.

 
 <img width="426" height="395" alt="image" src="https://github.com/user-attachments/assets/9dd3dd02-94fd-4301-a055-34e8e6a3bc65" />


 Silme butonu: İstenmeyen ürünleri listeden kaldırma.

 Arka planda stok kontrolü: Belirli aralıklarla otomatik stok takibi ve mail bildirimleri.


<img width="1917" height="575" alt="yelek stoğa geldi mail" src="https://github.com/user-attachments/assets/33697e13-2de7-448f-9e28-8559b9886c09" />

 JSON veri takibi: Ürün durumu ve stok değişikliklerinin detaylı kaydı.
