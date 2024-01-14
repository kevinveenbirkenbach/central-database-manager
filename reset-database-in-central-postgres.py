import subprocess
import argparse

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}\n{e.stderr}", file=sys.stderr)
        sys.exit(1)

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
        sys.exit(0)

def main(database_name, database_username):

    # Commands to drop and recreate the database
    postgres_commands = [
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'DROP DATABASE IF EXISTS {database_name};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'CREATE DATABASE {database_name};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'GRANT CREATE ON DATABASE {database_name} TO {database_username};'",
        f"docker exec central-postgres psql -v ON_ERROR_STOP=1 -U postgres -d {database_name} -c 'GRANT CREATE ON SCHEMA public TO {database_username};'"
    ]

    confirm_and_execute_commands(postgres_commands)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage a PostgreSQL database in a Docker container.")
    parser.add_argument("database_name", help="Name of the database")
    parser.add_argument("database_username", help="Username for database access")

    args = parser.parse_args()

    main(args.database_name, args.database_username)
