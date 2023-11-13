from auth import user_access
from ec2_controller import manage_ec2
from ebs_controller import manage_ebs
from s3_controller import manage_s3
from cloudwatch_controller import manage_cloudwatch
from rds_controller import manage_rds


def main_menu():
    "Main function for running the entire logic."
    while True:
        print("\nAWS Management Menu")
        print("1. Connect to AWS")
        print("2. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            valid, access_key, secret_key = user_access()
            region_choice = input("Enter the region to use (default is eu-west-1): ")
            if not region_choice.strip():
                region_choice = "eu-west-1"
            print(f"Selected region: {region_choice}")

            while True:
                if not valid:
                    break
                print("\nSelect a Menu")
                print("1. Manage EC2")
                print("2. Manage EBS")
                print("3. Manage S3")
                print("4. Manage Cloudwatch")
                print("5. Manage RDS")
                print("6. Back to Main Menu")

                service_choice = input("Enter your choice: ")
                if service_choice == "1":
                    manage_ec2(access_key, secret_key, region_choice)
                elif service_choice == "2":
                    manage_ebs(access_key, secret_key, region_choice)
                elif service_choice == "3":
                    manage_s3(access_key, secret_key, region_choice)
                elif service_choice == "4":
                    manage_cloudwatch(access_key, secret_key, region_choice)
                elif service_choice == "5":
                    manage_rds(access_key, secret_key, region_choice)
                elif service_choice == "6":
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
