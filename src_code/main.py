from auth import user_access
import boto3

def connect_to_aws():
    access_key = input("Enter your AWS Access Key ID: ")
    secret_key = input("Enter your AWS Secret Access Key: ")

    # Create a session using AWS credentials
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session 

def choose_menu():
    user_access()
    print("Select a menu: (1) EC2 instance, (2) EBS storage, (3) S3 Storage, (4) CloudWatch, (5) ELB")
    print("Select (0) to exit")

    while True:
        command = input("Enter menu number: ")

        try:
            command = int(command)  # Convert the input to an integer

            if command == 0:
                print("Thanks for using the menu system")
                break

            elif command == 1:
                print("Implementing EC2 instance functionalities")

            elif command == 2:
                print("Implementing EBS storage functionalities")

            elif command == 3:
                print("Implementing S3 storage functionalities")

            elif command == 4:
                print("Implementing CloudWatch functionalities")

            elif command == 5:
                print("Implementing ELB functionalities")

            else:
                print("Please enter a valid Menu Number.")

        except ValueError:
            print("Please enter a valid integer number.")

def main_menu():
    while True:
        print("\nAWS Management Menu")
        print("1. Connect to AWS")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            session = connect_to_aws()
            if session:
                while True:
                    print("\n1. Manage EC2")
                    print("2. Manage S3")
                    print("3. Back to Main Menu")

                    service_choice = input("Enter your choice: ")
                    if service_choice == "1":
                        manage_ec2(session)
                    elif service_choice == "2":
                        manage_s3(session)
                    elif service_choice == "3":
                        break  # Go back to the main menu
                    else:
                        print("Invalid choice. Please select a valid option.")
        elif choice == "2":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    choose_menu()


#tomorrow, add requirement.txt and implement the passwords and username part including adding new users as well. 