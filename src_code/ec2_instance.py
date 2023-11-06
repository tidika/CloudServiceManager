


class EC2Actions:

    def start_instance(self):
        print("start instance")
    def stop_instance(self):
        print("stop instance")
    def list_instance(self):
        print("list all the instances")



def manage_ec2():
    obj = EC2Actions()
    while True:

        print("\nSelect an EC2 action")
        print("1. List Instances")
        print("2. Start Instance")
        print("3. Stop Instance")
        print("4. Back to Services Menu")

        service_choice = input("Enter your choice: ")
        if service_choice == "1":
            obj.list_instance()
        elif service_choice == "2":
            obj.start_instance()
        elif service_choice == "3":
            obj.stop_instance()
        elif service_choice == "4":
            break  # Go back to the main menu
        else:
            print("Invalid choice. Please select a valid option.")

    
if __name__ == "__main__":
    manage_ec2()