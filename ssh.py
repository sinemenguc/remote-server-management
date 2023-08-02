import paramiko
import csv

def run_postgresql_query(ssh_client, service_name):
    if service_name == "jira":
        query = "SELECT * FROM urunler;"  #PostgreSQL Jira sorgusu
    elif service_name == "conf":
        query = "SELECT * FROM confluence_table;"  #PostgreSQL Confluence sorgusu
    elif service_name == "bitbucket":
        query = "SELECT * FROM bitbucket_table;"  #PostgreSQL Bitbucket sorgusu
    else:
        print("Hatalı servis seçimi.")
        return

    csv_file_path = "sonuc.csv"  #Uzak sunucuda oluşturulacak CSV dosyasının yolu

    #PostgreSQL sorgusunu çalıştır ve çıktısını CSV dosyasına yazdır
    ssh_client.exec_command(f'psql -U postgres -d deneme -t -A -F"," -c "{query}" > {csv_file_path}')

    return csv_file_path

def run_mysql_query(ssh_client, service_name):
    if service_name == "jira":
        query = "SELECT * FROM jira_table;"  #MySQL Jira sorgusu
    elif service_name == "conf":
        query = "SELECT * FROM confluence_table;"  #MySQL Confluence sorgusu
    elif service_name == "bitbucket":
        query = "SELECT * FROM bitbucket_table;"  #MySQL Bitbucket sorgusu
    else:
        print("Hatalı servis seçimi.")
        return

    csv_file_path = "/tmp/data.csv"  #Uzak sunucuda oluşturulacak CSV dosyasının yolu

    #MySQL sorgusunu çalıştır ve çıktısını CSV dosyasına yazdır
    ssh_client.exec_command(f'mysql -u root -p -e "{query}" > {csv_file_path}')

    return csv_file_path

def ssh_connect():
    remote_username = input("Lutfen hedef kullanici adini girin: ")
    ip_address = input("Lutfen hedef IP adresini girin: ")
    service_name = input("Lutfen hizmet adini girin (jira, bitbucket, conf): ")
    db_type = input("Lutfen veritabani turunu girin (mysql, pg): ")
    password = input(f"{remote_username}@{ip_address} icin parolanizi girin: ")

    #Remote bağlantıyı oluşturmak için paramiko kullanımı
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        #Girdileri kullanarak uzak sunucuya bağlantı sağlanıyor
        print("SSH baglantisi kuruluyor...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=5)
        print(f"{remote_username}@{ip_address} adresine baglanti basarili.")

        #Sorguyu çalıştır ve çıktısını CSV dosyasına yazdır
        if db_type == "pg":
            csv_file_path = run_postgresql_query(ssh_client, service_name)
        elif db_type == "mysql":
            csv_file_path = run_mysql_query(ssh_client, service_name)
        else:
            print("Hatalı veritabanı türü.")
            ssh_client.close()
            return

        #Olusturulan CSV dosyasini SFTP ile çekmek icin
        print("CSV dosyası SFTP ile cekiliyor...")
        with paramiko.Transport((ip_address, 22)) as transport:
            transport.connect(username=remote_username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(csv_file_path, "local_data.csv")
            sftp.close()
        print("CSV dosyası basariyla cekildi.")

        #Debian sunucusunda kal
        #print("SSH oturumu baslatılıyor...")
        #subprocess.run(f"ssh {remote_username}@{ip_address}", shell=True, check=True)
    except paramiko.AuthenticationException:
        print("Giris basarisiz. Kullanici adi veya sifre yanlis.")
    except paramiko.SSHException as e:
        print(f"SSH Hatasi: {e}")
    except Exception as e:
        print(f"Hata olustu: {e}")
    finally:
        ssh_client.close()

if __name__ == "__main__":
    print("Uzak sunucuya baglanma scriptine hosgeldiniz!")
    ssh_connect()