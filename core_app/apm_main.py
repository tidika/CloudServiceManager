import os

def provision_ec2_playbook(count, group_name):
    "ansible playbook provisions ec2 instances depending on the number specified by the user"

    playbook_path = '/home/ubuntu/provision_instances.yaml'  
    command = f"ansible-playbook {playbook_path} -e 'count={count}' -e 'group_name={group_name}'"
    os.system(command)

def install_apache():
    "installs apache server on ec2 instances selected by the user"

    playbook_path = '/home/ubuntu/install_apache.yaml'
    command = f"ansible-playbook {playbook_path}"
    os.system(command)
 

def main_menu():
    "Main function for running ansible playbooks."
    while True:
        print("\nWelcome to EC2 ansible playbook manager!!!")
        print("Select an Action")
        print("1. Provision EC2 Instances")
        print("2. Install Apache2 on EC2 Instances")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            count_input = input("Enter the number of EC2 to provision (1-5): ")
            try: 
                count = int(count_input)
                if 1 <= count <= 5:
                    group_name_input = input("Enter the group name: ")
                    provision_ec2_playbook(count, group_name_input)
                else:
                    print("Please enter a number between 1 and 5")
            except Exception as ex:
                print("Error: Unable to provision EC2 instances due to - ", ex)
        elif choice == "2":
            try:
                install_apache()
            except Exception as ex:
                print("Error: Unable to install apache2 due to - ", ex)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == "__main__":
    main_menu()

