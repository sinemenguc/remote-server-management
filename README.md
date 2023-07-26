# SSH ile Uzak Sunucuya Bağlanma ve Veri Aktarımı Scripti

Bu Python scripti, paramiko kütüphanesini kullanarak SSH protokolü üzerinden uzaktaki sunuculara bağlanmayı ve yönetmeyi sağlar.
Ayrıca, SFTP aracılığıyla veri aktarımı yapar ve bir CSV dosyasına veri yazma ve çekme işlemleri gerçekleştirir.

## Gereksinimler
+ Python3.x
+ paramiko kütüphanesi
+ csv kütüphanesi
+ subprocess kütüphanesi
## Kurulum
1. Bu projeyi klonlayın veya ZIP olarak indirin.
```
git clone https://github.com/sinemenguc/remote-server-management.git
```
2. Scriptin çalışması için gerekli olan **paramiko** ve **csv** kütüphanelerini yükleyin.
```
pip install paramiko
pip install csv
pip install subprocess
``` 
## Nasıl Kullanılır
1. Scripti çalıştırın:
```
python3 ssh.py
```
2. Ardından script, hedef kullanıcı adını, IP adresini ve oluşturmak istediğiniz dizinin adını isteyecektir.
3. Hedef sunucu için parolayı girin.
4. Script, uzak sunucuya SSH bağlantısını kuracak, belirtilen dizini oluşturacak ve içine bir CSV dosyası oluşturup verileri yazacaktır.
5. CSV dosyası başarıyla oluşturulduktan sonra, aynı dosya SFTP kullanılarak yerel bilgisayarınıza indirilecektir.
6. Eğer uzak sunucuda kalmak isterseniz, scriptteki ilgili son iki satırı yorum satırından çıkararak SSH oturumunuzu yeniden başlatabilirsiniz.

## Notlar
+ Script, doğru kullanıcı adı ve parola sağlanmadığında giriş başarısız mesajı verecektir.
+ Eğer hata oluşursa, ilgili hata mesajı görüntülenecektir.
---
Bu proje, uzaktaki sunucularla etkileşimde bulunmanıza ve veri aktarımı yapmanıza yardımcı olmak için oluşturulmuştur. Lütfen bu scripti sorumlu olmadığınız sistemlerde ve izin almadan kullanmaktan kaçının.

*Yazar*: *Sinem Mengüç*
