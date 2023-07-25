import paramiko #SSH protokolunu kullanarak uzaktaki sunuculara bağlanmayı ve yonetmeyi saglar
import subprocess #Yeni işlemler başlatmak ve sistem komutlarini calistirmak icin kullanilir
import csv #CSV dosyalarini okumak ve yazmak icin kullanilir

def ssh_connect():
    remote_username = input("Lutfen hedef kullanici adini girin: ")
    ip_address = input("Lutfen hedef IP adresini girin: ")
    directory_name = input("Olusturmak istediginiz dizinin adi: ")

    password = input(f"{remote_username}@{ip_address} icin parolanizi girin: ")

    #Remote bağlantıyı oluşturmak için paramiko kullanımı
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        #Girdileri kullanarak uzak sunucuya baglanti saglaniyor
        print("SSH baglantisi kuruluyor...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=5)
        print(f"{remote_username}@{ip_address} adresine baglanti basarili.")

        #Uzak sunucuda dizini oluştur
        print(f"{directory_name} adinda bir dizin olusturuluyor...")
        ssh_client.exec_command(f"mkdir {directory_name}")
        print(f"{directory_name} adinda bir dizin olusturuldu.")

        #SSH sunucusunda SFTP oturumu acma ve CSV dosyasini olusturup ve verileri yazma
        csv_file_path = f"{directory_name}/data.csv"
        with ssh_client.open_sftp().file(csv_file_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Sinem", "23", "DevOps Engineer"])
        ssh_client.close()

        #Olusturulan CSV dosyasini sftp ile cekmek icin
        print("CSV dosyası SFTP ile çekiliyor...")
        with paramiko.Transport((ip_address, 22)) as transport:
            transport.connect(username=remote_username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(csv_file_path, "local_data.csv")
            sftp.close()
        print("CSV dosyası basariyla cekildi.")

        #Debian sunucusunda kalmak istenirse asagidaki iki satirda yorumlari kaldirin
        # print("SSH oturumu başlatılıyor...")
        #subprocess.run(f"ssh {remote_username}@{ip_address}", shell=True, check=True)
    except paramiko.AuthenticationException:
        print("Giris basarisiz. Kullanici adi veya sifre yanlis.")
    except paramiko.SSHException as e:
        print(f"SSH Hatasi: {e}")
    except Exception as e:
        print(f"Hata olustu: {e}")

if __name__ == "__main__":
    print("SSH ile uzak sunucuya baglanma scriptine hos geldiniz!")
    ssh_connect()