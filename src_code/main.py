from auth import user_access
from resources import Resource
from ec2_instance import manage_ec2
import boto3


def connect_to_aws():
    access_key, secret_key = user_access()
    print(access_key, secret_key)
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name = "eu-west-1"
    )

    return session

# def manage_ec2():
#     # Placeholder function for managing EC2 instances
#     print("EC2 management options would be implemented here")

# def manage_s3():
#     # Placeholder function for managing S3 buckets and objects
#     print("S3 management options would be implemented here")


def main_menu():
    while True:
        print("\nAWS Management Menu")
        print("1. Connect to AWS")
        print("2. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            # session = connect_to_aws()
            access_key, secret_key = user_access()
            resource = Resource(access_key, secret_key)
            # print("The session value is this: ", session)
            while True:
                print("\nSelect a Menu")
                print("1. Manage EC2")
                print("2. Manage S3")
                print("3. Back to Main Menu")

                service_choice = input("Enter your choice: ")
                if service_choice == "1":
                    ec2 = resource.ec2_resource()
                    manage_ec2()
                elif service_choice == "2":
                    manage_s3()
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
    main_menu()


#tomorrow, include the right access key and secret key. Then push and make a pull request. 
#move on to developing the ec2_instance code and test they work as you progress. 