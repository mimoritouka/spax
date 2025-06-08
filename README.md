# Spax - Legal DoS Testing Tool

![Spax Banner](https://img.shields.io/badge/Spax-DoS%20Testing%20Tool-blue)

## Genel Bakış

**Spax**, hedef sistemlerin Dayanıklılık ve Güvenlik Testleri için geliştirilmiş bir **Yasal DoS (Denial of Service) Saldırı Simülatörüdür**. Bu araç, farklı saldırı yöntemlerini (HTTP, TCP, UDP, Slowloris) kullanarak sistemin dayanıklılığını ölçmek ve potansiyel zayıf noktaları tespit etmek için tasarlanmıştır.

> **UYARI:** Bu araç sadece eğitim ve yasal test amaçları için kullanılmalıdır. Yetkisiz kullanım yasa dışıdır ve ciddi hukuki sonuçlara yol açabilir.

---

## Özellikler

- HTTP, TCP, UDP ve Slowloris saldırı metodları
- Çoklu iş parçacığı (thread) desteği
- Saldırı süresini ayarlama imkanı (saniye bazında veya sınırsız)
- Canlı istatistik takibi (gönderilen istekler, başarılı/başarısız sayıları, RPS)
- Kullanıcı dostu komut satırı arayüzü ve batch script ile kolay kullanım
- Hedef URL/IP adresini otomatik çözümleme
- CTRL+C ile güvenli durdurma ve istatistik gösterimi

---

## Gereksinimler

- Python 3.8 veya üzeri
- Windows işletim sistemi (batch script desteği için)
- İnternet bağlantısı (hedef IP çözümleme için)

---

## Kullanım

### Batch Script (Windows)

1. `spax.py` ve `spax.bat` dosyalarını aynı klasörde olmalı.
2. `spax.bat` dosyasını çalıştırın.
3. Komut satırından hedef domain/IP, saldırı yöntemi, thread sayısı ve süre bilgilerini girin.
4. Saldırı başlatılır ve canlı istatistikler görüntülenir.
5. Saldırıyı durdurmak için `CTRL+C` kullanabilirsiniz.

---

### Komut Satırı Seçenekleri (Python Script)

```bash
python spax.py -d <target> [-m <method>] [-t <threads>] [-s <seconds>] [--quiet]
