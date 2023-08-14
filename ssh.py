import paramiko
import csv

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

def run_query(ssh_client, service_name, db_type, selected_database, csv_file_name):
    if db_type == "pg":
        if service_name == "jira":
            query = """
                SELECT p.pname as "Project Name", pr.name as "Role name", u.lower_user_name as "Username", u.display_name as "Display name", u.lower_email_address as "e-Mail", null as "Group name"
                FROM projectroleactor pra
                INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
                INNER JOIN project p ON p.ID = pra.PID
                INNER JOIN app_user au ON au.user_key = pra.ROLETYPEPARAMETER
                INNER JOIN cwd_user u ON u.lower_user_name = au.lower_user_name
                WHERE pra.roletype = 'atlassian-user-role-actor' and u.active = 1
                UNION
                SELECT p.pname as "Project Name", pr.name as "Role name", cmem.lower_child_name as "Username", u.display_name as "Display name", u.lower_email_address as "e-Mail", cmem.lower_parent_name as "Group name"
                FROM projectroleactor pra
                INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
                INNER JOIN project p ON p.ID = pra.PID
                INNER JOIN cwd_membership cmem ON cmem.parent_name = pra.roletypeparameter
                INNER JOIN app_user au ON au.lower_user_name = cmem.lower_child_name
                INNER JOIN cwd_user u ON u.lower_user_name = au.lower_user_name
                WHERE pra.roletype = 'atlassian-group-role-actor' and u.active = 1
                order by 1, 2, 3;
            """

            csv_file_path = f"{csv_file_name}.csv"
            ssh_client.exec_command(f'psql -U postgres -d {selected_database} -c "{query}"')
            return csv_file_path
        elif service_name == "conf":
            query = """
                 SELECT DISTINCT s.spaceid,
                 s.spacekey,
                 s.spacename,
                 cu.display_name,
                 sp.permgroupname AS groupname,
                 sp.permtype,
                 cg.local AS local_group,
                 cd.directory_name AS group_directory_name
                 FROM SPACES AS s
                 JOIN SPACEPERMISSIONS AS sp ON s.spaceid = sp.spaceid
                 LEFT JOIN user_mapping AS u ON sp.permusername = u.user_key
                 LEFT JOIN cwd_user AS c ON c.lower_user_name = u.lower_username
                 LEFT JOIN cwd_group AS cg ON sp.permgroupname = cg.group_name
                 LEFT JOIN cwd_directory AS cd ON cg.directory_id = cd.id
                 LEFT JOIN cwd_membership AS cm ON cg.id = cm.parent_id
                 LEFT JOIN cwd_user AS cu ON cu.id = cm.child_user_id
                 WHERE s.spacestatus = 'CURRENT' and cu.active = 'T'
                 AND cu.lower_user_name IS NOT NULL
                 ORDER BY spacekey,groupname;
             """
        elif service_name == "bitbucket":
            query = "SELECT * FROM musteriler WHERE id = 3;"
        else:
            print("Invalid service selection.")
            return

        csv_file_path = f"{csv_file_name}.csv"
        ssh_client.exec_command(f'psql -U postgres -d {selected_database} -t -A -F"," -c "{query}" > {csv_file_path}')
        return csv_file_path

    elif db_type == "mysql":
        if service_name == "jira":
            query = """
                 SELECT p.pname as "Project Name", pr.name as "Role name", u.lower_user_name as "Username", u.display_name as "Display name", u.lower_email_address as "e-Mail", null as "Group name"
                 FROM projectroleactor pra
                 INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
                 INNER JOIN project p ON p.ID = pra.PID
                 INNER JOIN app_user au ON au.user_key = pra.ROLETYPEPARAMETER
                 INNER JOIN cwd_user u ON u.lower_user_name = au.lower_user_name
                 WHERE pra.roletype = 'atlassian-user-role-actor' and u.active = 1)
                 UNION
                 SELECT p.pname as "Project Name", pr.name as "Role name", cmem.lower_child_name as "Username", u.display_name as "Display name", u.lower_email_address as "e-Mail", cmem.lower_parent_name as "Group name"
                 FROM projectroleactor pra
                 INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
                 INNER JOIN project p ON p.ID = pra.PID
                 INNER JOIN cwd_membership cmem ON cmem.parent_name = pra.roletypeparameter
                 INNER JOIN app_user au ON au.lower_user_name = cmem.lower_child_name
                 INNER JOIN cwd_user u ON u.lower_user_name = au.lower_user_name
                 WHERE pra.roletype = 'atlassian-group-role-actor' and u.active = 1
                 order by 1, 2, 3;
             """
        elif service_name == "conf":
            query = """
                 SELECT DISTINCT s.spaceid,
                 s.spacekey,
                 s.spacename,
                 cu.display_name,
                 sp.permgroupname AS groupname,
                 sp.permtype,
                 cg.local AS local_group,
                 cd.directory_name AS group_directory_name
                 FROM SPACES AS s
                 JOIN SPACEPERMISSIONS AS sp ON s.spaceid = sp.spaceid
                 LEFT JOIN user_mapping AS u ON sp.permusername = u.user_key
                 LEFT JOIN cwd_user AS c ON c.lower_user_name = u.lower_username
                 LEFT JOIN cwd_group AS cg ON sp.permgroupname = cg.group_name
                 LEFT JOIN cwd_directory AS cd ON cg.directory_id = cd.id
                 LEFT JOIN cwd_membership AS cm ON cg.id = cm.parent_id
                 LEFT JOIN cwd_user AS cu ON cu.id = cm.child_user_id
                 WHERE s.spacestatus = 'CURRENT' and cu.active = 'T'
                 AND cu.lower_user_name IS NOT NULL
                 ORDER BY spacekey,groupname;
             """
        elif service_name == "bitbucket":
            query = """
                 (SELECT DISTINCT p.id                                       AS "Project ID",
                          p.name                                     AS "Project Name",
                          r.name                                     AS "Repo Name",
                          cu.id                                      AS "User ID (Individual)",
                          cu.user_name                               AS "Username (Individual)",
                          Concat(cu.first_name, ' ', cu.last_name)   AS "Fullname (Individual)",
                          pp.perm_id                                 AS "Permission Type"
                 FROM   project p
                    JOIN sta_normal_project np
                     ON np.project_id = p.id
                    LEFT JOIN sta_project_permission pp
                         ON pp.project_id = p.id
                    LEFT JOIN repository r
                         ON r.project_id = p.id
                    LEFT JOIN sta_repo_permission srp
                         ON srp.repo_id = r.id
                    LEFT JOIN sta_normal_user u
                         ON srp.user_id = u.user_id
                    LEFT JOIN cwd_user cu
                         ON cu.lower_user_name = u.name

                 WHERE  srp.group_name IS NOT NULL  OR srp.user_id IS NOT NULL)

                 UNION
                 SELECT DISTINCT p.id                                       AS "Project ID",
                         p.name                                     AS "Project Name",
                         ''                                         AS "Repo Name",
                         cu.id                                      AS "User ID (Individual)",
                         cu.user_name                               AS "Username (Individual)",
                         Concat(cu.first_name, ' ', cu.last_name)   AS "Fullname (Individual)",
                         pp.perm_id                                 AS "Permission Type"
                 FROM   project p
                    JOIN sta_normal_project np
                     ON np.project_id = p.id
                    LEFT JOIN sta_project_permission pp
                          ON pp.project_id = p.id
                    LEFT JOIN sta_normal_user u
                          ON pp.user_id = u.user_id
                    LEFT JOIN cwd_user cu
                          ON cu.lower_user_name = u.name
                 WHERE  pp.group_name IS NOT NULL  OR pp.user_id IS NOT NULL;
             """
        else:
            print("Invalid service selection.")
            return

        csv_file_path = f"{csv_file_name}.csv"
        mysql_command = f'mysql -u debian -D {selected_database} -e "{query}" > {csv_file_path}'
        ssh_client.exec_command(mysql_command)
        return csv_file_path
    else:
        print("Invalid database type.")
        return

def ssh_connect():
    ip_address = input("Please enter the target IP address: ")
    remote_username = input("Please enter the target username: ")
    password = input(f"Enter your password for {remote_username}@{ip_address}: ")
    service_name = input("Please enter the service name (jira, bitbucket, conf): ")
    db_type = input("Please enter the database type (mysql, pg): ")
    csv_file_name = input("Enter the CSV file name: ")
    csv_file_path = f"{csv_file_name}.csv"

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Establishing SSH connection...")
        ssh_client.connect(hostname=ip_address, username=remote_username, password=password, timeout=60)
        print(f"Connected to {remote_username}@{ip_address}.")
        list_databases(ssh_client, db_type)
        selected_database = input("Please select the database to connect to: ")
        if db_type == "pg" or db_type == "mysql":
            csv_file_path = run_query(ssh_client, service_name, db_type, selected_database, csv_file_name)
        else:
            print("Invalid database type.")
            ssh_client.close()
            return

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

if __name__ == "__main__":
    print("Welcome to the remote server connection script!")
    ssh_connect()