from auth import user_access
from ec2_controller import manage_ec2


def main_menu():
    "Main function for running the entire logic. "
    while True:
       
        print("\nAWS Management Menu")
        print("1. Connect to AWS")
        print("2. Exit")

        choice = input("Enter your choice: ")
        
        if choice == "1":
            valid, access_key, secret_key = user_access()

            while True:
                if not valid:
                    break
                print("\nSelect a Menu")
                print("1. Manage EC2")
                print("2. Manage S3")
                print("3. Back to Main Menu")

                service_choice = input("Enter your choice: ")
                if service_choice == "1":
                    manage_ec2(access_key, secret_key)
                elif service_choice == "2":
                    pass
                elif service_choice == "3":
                    break  
                else:
                    print("Invalid choice. Please select a valid option.")
        elif choice == "2":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()


