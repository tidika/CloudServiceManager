
from interface import Resource,Client
from utils import categorize_ec2_response, show_instances


class EC2Actions:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.ec2_client = Client(access_key, secret_key).ec2_client()
        self.instance_ids = {
                "1": "i-03aeb95ee2eb5d041",
                "2": "i-06fc919515f7a6260"
            }


    def list_instance(self):
        "Lists all the instances within an aws account"
        region_running_instances = {}
        region_other_instances = {}

        regions = [region['RegionName'] for region in self.ec2_client.describe_regions()['Regions']]

        for region in regions:
            ec2_region_client = Client(self.access_key, self.secret_key,region).ec2_client()
            response = ec2_region_client.describe_instances()
            running_instances, other_instances = categorize_ec2_response(response)

            if running_instances: 
                region_running_instances[region] = running_instances
            if other_instances:
                region_other_instances[region] = other_instances

            region_running_instances[region] = running_instances
            region_other_instances[region] = other_instances
        
        print("\n*****************************Running Instances*********************************")
        for region, instances in region_running_instances.items():
            if instances:
                print(f"Region: {region}")
                print(instances)

        print("\n*****************************Other Instances************************************")
        for region, instances in region_other_instances.items():
            if instances:
                print(f"Region: {region}")
                print(instances)
    

    def start_instance(self):
        "starts a specified instance"
        while True:
            show_instances()
            choice = input("Enter your choice: ")

            if choice in self.instance_ids:
                instance_id = self.instance_ids[choice]
                try:
                    self.ec2_client.start_instances(InstanceIds=[instance_id])
                    print(f"\nStarting the instance with ID {instance_id}. Please wait for it to become operational...")
                    waiter = self.ec2_client.get_waiter('instance_running')
                    waiter.wait(InstanceIds=[instance_id])
                    print(f"Instance with ID {instance_id} is running.")

                except Exception as ex:
                    print("Error: Unable to start the instance:", ex)
            
            elif choice == "3":
                break

            else:
                print("Invalid choice. Please select a valid option.")
            
    def stop_instance(self):
        "Stops a specified instance"
        while True:
            show_instances()
            choice = input("Enter your choice: ")

            if choice in self.instance_ids:
                instance_id = self.instance_ids[choice]
                try:
                    self.ec2_client.stop_instances(InstanceIds=[instance_id])
                    print(f"\nStopping the instance with ID {instance_id}. Please wait for it to come to a stop...")
                    waiter = self.ec2_client.get_waiter('instance_stopped')
                    waiter.wait(InstanceIds=[instance_id])
                    print(f"The instance {instance_id} has been successfully stopped.")
                except Exception as ex:
                    print("Error: Unable to stop the instance:", ex)
            
            elif choice == "3":
                break

            else:
                print("Invalid choice. Please select a valid option.")

    def launch_instance(self):
        "Launches a specified instance"
        launch_details = {"1": "ami-0e309a5f3a6dd97ea", "2":"ami-04c320a393da4b1ba"}

        while True:
            print("\nSelect AMI Type")
            print("1. Linux")
            print("2. Windows")
            print("3. Back to EC2 action Menu")
            choice = input("Enter your choice:").lower()

            if choice in launch_details:
                image_id = launch_details[choice]
                response = self.ec2_client.run_instances(
                    ImageId=image_id,
                    InstanceType="t3.micro",
                    KeyName="COMP8062",
                    MaxCount=1,
                    MinCount=1
                )

                instance_id = response['Instances'][0]['InstanceId']
                print("The created instance id is: ",instance_id)

            elif choice == "3":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def terminate_instance(self):
        "Terminates a specified instance"
        while True:
            show_instances()
            choice = input("Enter your choice: ")

            if choice in self.instance_ids:
                instance_id = self.instance_ids[choice]
                try:
                    self.ec2_client.terminate_instances(InstanceIds=[instance_id])
                    print(f"\nterminating the instance with ID {instance_id}. Please wait for it to fully terminate...")
                    waiter = self.ec2_client.get_waiter('instance_terminated')
                    waiter.wait(InstanceIds=[instance_id])
                    print(f"The instance {instance_id} has been successfully terminated.")
                 
                except Exception as ex:
                    print("Error: Unable to terminate the instance:", ex)
            
            elif choice == "3":
                break

            else:
                print("Invalid choice. Please select a valid option.")


def manage_ec2(access_key, secret_key):
    action = EC2Actions(access_key, secret_key)
    while True:

        print("\nSelect an EC2 action")
        print("1. List Instances")
        print("2. Start Instance")
        print("3. Stop Instance")
        print("4. Launch Instance")
        print("5. terminate Instance")
        print("6. Back to Services Menu")

        service_choice = input("Enter your choice: ")
        if service_choice == "1":
            action.list_instance()
        elif service_choice == "2":
           action.start_instance()
        elif service_choice == "3":
            action.stop_instance()
        elif service_choice == "4":
            action.launch_instance()
        elif service_choice == "5":
            action.terminate_instance()
        elif service_choice == "6":
            break  
        else:
            print("Invalid choice. Please select a valid option.")

    
if __name__ == "__main__":
    manage_ec2()