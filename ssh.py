import paramiko
import csv

def list_databases(ssh_client, db_type):
    if db_type == "pg":
        command = "psql -U postgres -l"
    elif db_type == "mysql":
        command = "mysql -u debian -e 'SHOW DATABASES;'"
    else:
        print("Hatalı veritabanı türü.")
        return

    _, stdout, _ = ssh_client.exec_command(command)
    databases = stdout.read().decode("utf-8")

    print("Mevcut veritabanları:")
    print(databases)

def run_query(ssh_client, service_name, db_type, selected_database):
    if db_type == "pg":
        if service_name == "jira":
            query = "SELECT * FROM urunler;"
        elif service_name == "conf":
            query = "SELECT * FROM users;"
        elif service_name == "bitbucket":
            query = "SELECT * FROM musteriler WHERE id = 3;"
        else:
            print("Hatalı servis seçimi.")
            return

        csv_file_path = "sonuc.csv"  #Uzak sunucuda oluşturulacak CSV dosyasının yolu

        #PostgreSQL sorgusunu çalıştır ve çıktısını CSV dosyasına yazdır
        ssh_client.exec_command(f'psql -U postgres -d {selected_database} -t -A -F"," -c "{query}" > {csv_file_path}')

        return csv_file_path

    elif db_type == "mysql":
        if service_name == "jira":
            query = "SELECT * FROM posts;"
        elif service_name == "conf":
            query = "SELECT * FROM confluence_table;"
        elif service_name == "bitbucket":
            query = "SELECT * FROM bitbucket_table;"
        else:
            print("Hatalı servis seçimi.")
            return

        csv_file_path = "mysqlsonuc.csv"  #Uzak sunucuda oluşturulacak CSV dosyasının yolu

        #MySQL sorgusunu çalıştır ve çıktısını CSV dosyasına yazdır
        mysql_command = f'mysql -u debian -D {selected_database} -e "{query}" > {csv_file_path}'
        ssh_client.exec_command(mysql_command)
        return csv_file_path
    else:
        print("Hatalı veritabanı türü.")
        return

def ssh_connect():
    remote_username = input("Lütfen hedef kullanıcı adını girin: ")
    ip_address = input("Lütfen hedef IP adresini girin: ")
    service_name = input("Lütfen hizmet adını girin (jira, bitbucket, conf): ")
    db_type = input("Lütfen veritabanı türünü girin (mysql, pg): ")
    password = input(f"{remote_username}@{ip_address} için parolanızı girin: ")

    #Remote bağlantıyı oluşturmak için paramiko kullanımı
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        #Girdileri kullanarak uzak sunucuya bağlantı sağlanıyor
        print("SSH bağlantısı kuruluyor...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=5)
        print(f"{remote_username}@{ip_address} adresine bağlantı başarılı.")

        #Veritabanlarını listeleyelim
        list_databases(ssh_client, db_type)

        #İstediği veritabanına bağlanalım ve sorguyu çalıştıralım
        selected_database = input("Lütfen bağlanmak istediğiniz veritabanını seçin: ")
        if db_type == "pg" or db_type == "mysql":
            csv_file_path = run_query(ssh_client, service_name, db_type, selected_database)
        else:
            print("Hatalı veritabanı türü.")
            ssh_client.close()
            return

        #Olusturulan CSV dosyasini SFTP ile çekmek için...
        print("CSV dosyası SFTP ile çekiliyor...")
        with paramiko.Transport((ip_address, 22)) as transport:
            transport.connect(username=remote_username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(csv_file_path, "local_data.csv")
            sftp.close()
        print("CSV dosyası başarıyla çekildi.")

    except paramiko.AuthenticationException:
        print("Giriş başarısız. Kullanıcı adı veya şifre yanlış.")
    except paramiko.SSHException as e:
        print(f"SSH Hatası: {e}")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        ssh_client.close()

if __name__ == "__main__":
    print("Uzak sunucuya bağlanma scriptine hoş geldiniz!")
    ssh_connect()