def get_credentials():
    "gets username and password data from user"

    username = input("Enter your username: ")
    password = input("Enter your password: ")
    return username, password


def get_optional_aws_credentials():
    "gets aws access key and secret key from user"

    access_key = input("Enter your AWS access key (optional): ")
    secret_key = input("Enter your AWS secret key (optional): ")
    return access_key, secret_key


def store_credentials(username, password, aws_accesskey=None, aws_secretkey=None):
    "stores the credentials received from user to password.txt"
    try:
        with open("password.txt", "a") as file:
            file.write(f"{username}\t{password}\t{aws_accesskey}\t{aws_secretkey}\n")
    except Exception as ex:
        print(f"An error occurred while writing credentials to file: {ex}")


def fetch_credentials(filename="password.txt"):
    "retrieves user credential from password.txt"
    try:
        with open(filename, "r") as file:
            data = file.readlines()
            data = [
                line.strip() for line in data if line.strip()
            ]  # to strip newline characters and filter non-empty lines.
        return data
    except FileNotFoundError:
        print(f"File '{filename}' not found.")


def authenticate_user(username, password):
    "authenticates user using user provided username and password"
    valid = False
    data = fetch_credentials()
    access_key, secret_key = None, None

    if data:
        for line in data:
            parts = line.strip().split()
            stored_username, stored_password, *access_keys = parts
            if (username == stored_username) and (password == stored_password):
                access_key = access_keys[0] if access_keys else None  # Assign access_key
                secret_key = access_keys[1:] if len(access_keys) > 1 else None  # Assign secret_key
                valid = True 
                break
        return valid, access_key, secret_key


def register_new_user():
    "registers a new user"
    username, password = get_credentials()
    access_key, secret_key = get_optional_aws_credentials()
    store_credentials(username, password, access_key, secret_key)


def login():
    "logs in a user to the system"
    while True:
        username, password = get_credentials()

        if not username or not password:
            print("Empty username and/or password")
            break

        else:
            valid, access_key, secret_key = authenticate_user(username, password)

            if valid:
                print("Authentication successful. You are logged in!")
                break
            
            else:
                print("Authentication failed. Please check your credentials.")
                command = input("Do you want to (E)xit or (C)ontinue? ").lower()
                if command == "e":
                    break
    return access_key, secret_key                

def user_access():
    "manages user login and registration"
    while True:
        user_status = input("Are you a returning user? (yes/no): ").lower()

        if user_status == "yes":
            access_key, secret_key = login()
            break

        elif user_status == "no":
            print("\nWelcome, it seems you are a new user.")
            print("Let's start the registration process.")
            register_new_user()
            print("Registration successful. Please proceed to log in.")
            login()
            break

        elif user_status == "exit":
            print("Thanks for using the system. ")

        else:
            print(
                "Wrong input detected. Please enter 'yes' or 'no' or type 'exit' to quit"
            )
    return access_key, secret_key

if __name__ == "__main__":
    access_key, secret_key = user_access()
#    valid,  access, secret = authenticate_user("Tochi", "idika2021")
#    print(valid)
#    print(access)
#    print(secret)


#try to use the wrong password and see what error message you get. and see if there is a way to fix 
#Tommorrow run the authenticte_user code directly and see if that works, then try to fix the issue above
#lactivate your git and start pushing this work github to have a copy there. 
#work on finishing your main.py file so you can start developing each module. 