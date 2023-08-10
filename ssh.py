#Import the required modules
import paramiko
import csv

#Function to list databases on the remote server
def list_databases(ssh_client, db_type):
    if db_type == "pg":
        command = "psql -U postgres -l"
    elif db_type == "mysql":
        command = "mysql -u debian -e 'SHOW DATABASES;'"
    else:
        print("Invalid database type.")
        return

    _, stdout, _ = ssh_client.exec_command(command)
    databases = stdout.read().decode("utf-8")

    print("Available databases:")
    print(databases)

#Function to run a query on the selected database and save results to a CSV file
def run_query(ssh_client, service_name, db_type, selected_database, csv_file_name):
    if db_type == "pg":
        #Define queries based on service_name
        if service_name == "jira":
            query = "SELECT * FROM urunler;"
        elif service_name == "conf":
            query = "SELECT * FROM users;"
        elif service_name == "bitbucket":
            query = "SELECT * FROM musteriler WHERE id = 3;"
        else:
            print("Invalid service selection.")
            return

        csv_file_path = f"{csv_file_name}.csv"  #Path for the remote CSV file

        #Run PostgreSQL query and save output to a CSV file
        ssh_client.exec_command(f'psql -U postgres -d {selected_database} -t -A -F"," -c "{query}" > {csv_file_path}')
        return csv_file_path

    elif db_type == "mysql":
        #Define queries based on service_name
        if service_name == "jira":
            query = "SELECT * FROM posts;"
        elif service_name == "conf":
            query = "SELECT * FROM confluence_table;"
        elif service_name == "bitbucket":
            query = "SELECT * FROM bitbucket_table;"
        else:
            print("Invalid service selection.")
            return

        csv_file_path = f"{csv_file_name}.csv"  #Path for the remote CSV file

        #Run MySQL query and save output to a CSV file
        mysql_command = f'mysql -u debian -D {selected_database} -e "{query}" > {csv_file_path}'
        ssh_client.exec_command(mysql_command)
        return csv_file_path
    else:
        print("Invalid database type.")
        return

#Function to establish an SSH connection
def ssh_connect():
    remote_username = input("Please enter the target username: ")
    ip_address = input("Please enter the target IP address: ")
    service_name = input("Please enter the service name (jira, bitbucket, conf): ")
    db_type = input("Please enter the database type (mysql, pg): ")
    password = input(f"Enter your password for {remote_username}@{ip_address}: ")
    csv_file_name = input("Enter the CSV file name: ")
    csv_file_path = f"{csv_file_name}.csv"  #Create a CSV file with the given name

    #Create an SSH client using paramiko
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        #Establish an SSH connection to the remote server using the provided inputs
        print("Establishing SSH connection...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=5)
        print(f"Connected to {remote_username}@{ip_address}.")

        #List the available databases
        list_databases(ssh_client, db_type)

        #Connect to the selected database and run the query
        selected_database = input("Please select the database to connect to: ")
        if db_type == "pg" or db_type == "mysql":
            csv_file_path = run_query(ssh_client, service_name, db_type, selected_database, csv_file_name)
        else:
            print("Invalid database type.")
            ssh_client.close()
            return

        #Retrieve the generated CSV file using SFTP
        print("Retrieving CSV file using SFTP...")
        with paramiko.Transport((ip_address, 22)) as transport:
            transport.connect(username=remote_username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get(csv_file_path, f"{csv_file_name}.csv")
            sftp.close()
        print("CSV file successfully retrieved.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Incorrect username or password.")
    except paramiko.SSHException as e:
        print(f"SSH Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh_client.close()

#Main entry point
if __name__ == "__main__":
    print("Welcome to the remote server connection script!")
    ssh_connect()