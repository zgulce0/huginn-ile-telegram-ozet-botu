📚 Telegram PDF Özetleyici Bot Projesi (Huginn + Python + Ollama)

Bu proje; Telegram üzerinden gönderilen PDF dosyalarını yapay zeka kullanarak otomatik olarak özetleyen akıllı bir otomasyon sistemidir. Sistem tamamen bilgisayarınızda (yerel olarak) çalışır ve verilerinizi dışarıya aktarmaz.

---

## 🧭 Sistemin Çalışma Mantığı (Nasıl Çalışır?)

Sistemimiz birbirine bağlı 4 farklı programın (Docker Konteyneri) ve Huginn içindeki 5 farklı ajanın bir zincir oluşturmasıyla çalışır:

1. **Giriş (Telegram):** Siz bota bir PDF gönderirsiniz.
2. **Yakalama (Huginn):** Huginn bu PDF'i havada yakalar ve içindeki dosya numarasını alır.
3. **İşleme (Python):** Python arka planda PDF'i bilgisayarınıza indirir ve içindeki yazıları tek tek okur.
4. **Zeka (Ollama):** Okunan yazılar bilgisayarınızdaki Llama3 yapay zeka modeline gönderilir ve Türkçe özeti çıkartılır.
5. **Çıkış (Telegram):** Hazırlanan özet yine Huginn üzerinden Telegram ekranınıza mesaj olarak gelir.

---

## 🛠️ Adım Adım Kurulum Rehberi

Sistemi sıfırdan kurarken ya da bilgisayar uykudan uyandığında ajanlar silindiyse aşağıdaki sırayla ilerleyin:

### 1. Aşama: Altyapıyı Hazırlamak (Docker Kontrolleri)
* Komut satırından `pdf-processor` konteynerinin doğru Telegram tokenı ile başlatıldığından emin olun.
* Yapay zekanın çalışabilmesi için Ollama içine `llama3` modelinin indirilmiş olduğundan emin olun. (Eğer özetler "Özet çıkarılamadı" şeklinde dönüyorsa bu model henüz yüklenmemiş demektir).

### 2. Aşama: Huginn Ajan Zincirini Kurmak

Huginn arayüzüne girip sırasıyla şu 5 ajanı oluşturun:

* **1- Telegram Webhook (Webhook Agent):** Telegram botundan gelecek mesajları ilk karşılayan kapıdır. Bu ajanı oluşturduğunuzda size özel bir internet adresi (URL) verir. Bu adresi Telegram botunuza "webhook" olarak tanımlamanız gerekir.
* **2- Sadece PDF Seç (Trigger Agent):** 1. ajana bağlı çalışır. Gelen mesajın boş bir yazı mı yoksa gerçekten bir PDF dosyası mı olduğunu kontrol eder. İçinde dosya olmayan mesajları çöpe atar.
* **3- Python'a Gönder (Post Agent):** 2. ajana bağlı çalışır. PDF'in kimlik bilgilerini, işlenmesi için arka plandaki Python programına postalar. 
* **4- Özet Yakalayıcı (Webhook Agent):** Python programı PDF'i indirip özetleme işini bitirdiğinde, hazırladığı özeti Huginn'e teslim etmek için bu ajanın kapısını çalar.
* **5- Telegram Cevap (Post Agent):** 4. ajana bağlı çalışır. Gelen Türkçe özeti alır ve Telegram üzerinden sizin chat ekranınıza nihai mesaj olarak gönderir.

---

## ⚠️ Dikkat Edilmesi Gereken En Kritik Nokta (Zinciri Bağlamak)

Ajanları kurarken en çok yapılan hata bağlantıyı unutmaktır. 
* **4- Özet Yakalayıcı** ajanını kurup kaydettiğinizde sistem size üst menüde uzun bir URL adresi verecektir. 
* O adresi kopyalayıp, **3- Python'a Gönder** ajanının ayarlarındaki `webhook_url` kısmına yapıştırmalısınız. Bu iki ajan birbirine bu linkle bağlanır. Eğer bunu yapmazsanız Python özeti hazırlar ama Huginn'e geri teslim edemez.

---<img width="1188" height="412" alt="WhatsApp Image 2026-06-05 at 22 35 28" src="https://github.com/user-attachments/assets/075bf0cf-759c-4d1e-8c61-c1606be3293b" />


* **Telegram'a hiçbir mesaj gelmiyor:** 1. ajanın (Webhook) açık olduğunu ve Telegram botunuza doğru şekilde bağlandığını kontrol edin.
* **Mesaj geliyor ama "Özet çıkarılamadı" yazıyor:** Altyapı bağlantılarınız harika çalışıyor demektir. Tek sorun, yapay zekanın (Ollama) içinde Llama3 modelinin yüklü olmamasıdır. Ollama'ya modeli yüklediğinizde bu sorun tamamen çözülür.
* **Bilgisayarı kapatıp açınca her şey sıfırlandı:** Veritabanı kalıcı olarak bilgisayara bağlanmadığı için Huginn ilk günkü haline dönebilir. Bu durumda yukarıdaki 5 ajanı sırasıyla yeniden oluşturmanız gerekir.
