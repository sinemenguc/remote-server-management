import paramiko
import subprocess
import csv

def ssh_connect():
    remote_username = input("Lütfen hedef kullanıcı adını girin (Debian tarafında): ")
    ip_address = input("Lütfen hedef IP adresini girin: ")
    directory_name = input("Oluşturmak istediğiniz dizinin adı: ")

    password = input(f"{remote_username}@{ip_address} için parolanızı girin: ")

    # Remote bağlantıyı oluşturmak için paramiko kullanımı
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("SSH bağlantısı kuruluyor...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=5)
        print(f"{remote_username}@{ip_address} adresine bağlantı başarılı.")

        # Uzakta dizini oluştur
        print(f"{directory_name} adında bir dizin oluşturuluyor...")
        ssh_client.exec_command(f"mkdir {directory_name}")
        print(f"{directory_name} adında bir dizin oluşturuldu.")

        # CSV dosyasını oluştur ve verileri yaz
        csv_file_path = f"{directory_name}/data.csv"
        with ssh_client.open_sftp().file(csv_file_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["Sinem", "23", "DevOps Engineer"])
            # Burada dilediğiniz verileri CSV dosyasına yazabilirsiniz

        ssh_client.close()

        # Oluşturulan CSV dosyasını sftp ile çek
        print("CSV dosyası SFTP ile çekiliyor...")
        with paramiko.Transport((ip_address, 22)) as transport:
            transport.connect(username=remote_username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(csv_file_path, "localdeki_data.csv")
            sftp.close()
        print("CSV dosyası başarıyla çekildi.")

        # Debian sunucusunda kal
        print("SSH oturumu başlatılıyor...")
        subprocess.run(f"ssh {remote_username}@{ip_address}", shell=True, check=True)
    except paramiko.AuthenticationException:
        print("Giriş başarısız. Kullanıcı adı veya şifre yanlış.")
    except paramiko.SSHException as e:
        print(f"SSH Hatası: {e}")
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    print("Debian WSL'e SSH ile bağlanma scriptine hoş geldiniz!")
    ssh_connect()