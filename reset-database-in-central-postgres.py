import subprocess
import argparse
import sys

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{e.stderr}", file=sys.stderr)
        exit(1)

def confirm_and_execute_commands(commands):
    print("The following commands will be executed:")
    for cmd in commands:
        print(cmd)
    confirm = input("Do you want to execute these commands? (yes/no): ").strip().lower()
    if confirm == "yes":
        for cmd in commands:
            execute_command(cmd)
    else:
        print("Operation cancelled.")
        exit(0)

def prepare_postgres_commands(database_name, database_username):
    return [
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'DROP DATABASE IF EXISTS {database_name};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'CREATE DATABASE {database_name};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'GRANT CREATE ON DATABASE {database_name} TO {database_username};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -d {database_name} -c 'GRANT CREATE ON SCHEMA public TO {database_username};'"
    ]

def prepare_mariadb_commands(database_type, database_name, database_username, database_password):
    password_option = f"-p'{database_password}'" if database_password else ""
    return [
        f"docker exec central-mariadb {database_type} -u root {password_option} -e 'DROP DATABASE IF EXISTS {database_name};'",
        f"docker exec central-mariadb {database_type} -u root {password_option} -e 'CREATE DATABASE {database_name};'",
        f"docker exec central-mariadb {database_type} -u root {password_option} -e 'GRANT ALL PRIVILEGES ON {database_name}.* TO {database_username};'"
    ]

def main(database_type, database_name, database_username, database_password=None):
    if database_username is None:
        database_username = database_name
    database_type_lower = database_type.lower()
    if database_type_lower == "postgres":
        commands = prepare_postgres_commands(database_name, database_username)
    elif database_type_lower in ["mariadb", "mysql"]:
        commands = prepare_mariadb_commands(database_type_lower, database_name, database_username, database_password)
    else:
        print("Unsupported database type. Supported types are 'postgres' and 'mariadb'.")
        exit(2)
        
    confirm_and_execute_commands(commands)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage a PostgreSQL or MariaDB database in a Docker container.")
    parser.add_argument("database_type", choices=["postgres", "mariadb", "mysql"], help="Type of the database (postgres or mariadb)")
    parser.add_argument("database_name", help="Name of the database")
    parser.add_argument("database_username", nargs='?', default=None, help="Username for database access (optional, defaults to database name)")
    parser.add_argument("--database_password", help="Password for the MariaDB root account (optional)")

    args = parser.parse_args()
    main(args.database_type, args.database_name, args.database_username, args.database_password)