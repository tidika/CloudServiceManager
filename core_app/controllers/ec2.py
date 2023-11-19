from interface import Client
from utils import categorize_ec2_response


class EC2Actions:
    "This class encapsulates methods essential for managing and interacting with an EC2 instance."

    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ec2_client = Client(access_key, secret_key, region).ec2_client()

    def list_instances(self):
        "Enumerates instances either within the user's AWS account or the logged-in region."
        print("\nSelect a list action")
        print("1. List all instances within the aws account")
        print(f"2. List instances in the {self.region} region")
        print("3. Back to EC2 actions Menu")

        while True:
            choice = input("Enter your choice: ")

            if choice == "1":
                self.list_all_instances()
            elif choice == "2":
                self.list_region_instances()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def start_instance(self):
        "Starts up an EC2 instance specified by the user"
        while True:
            print("\nSelect an Instance ID")
            running_instance, stopped_instance = self.list_instanceId()
            print("")
            choice = input(
                "Enter your instance ID choice (or type 'exit' to go back to ec2 action menu): "
            )

            if choice in stopped_instance:
                self.start_instance_util(choice)
                return None
            elif choice in running_instance:
                print("The instance is already in a running state")
            elif choice == "exit":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def stop_instance(self):
        "Stops an EC2 instance specified by the user"
        while True:
            print("\nSelect an Instance ID")
            running_instance, stopped_instance = self.list_instanceId()
            print("")
            choice = input(
                "Enter your instance ID choice (or type 'exit' to go back to ec2 action menu): "
            )

            if choice in running_instance:
                self.stop_instance_util(choice)
                return None
            elif choice in stopped_instance:
                print("The instance is already in a stopped state")
            elif choice == "exit":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def launch_instance(self):
        "Launches an EC@ instance based on the ami type selected by the user."
        launch_details = {"1": "ami-0e309a5f3a6dd97ea", "2": "ami-04c320a393da4b1ba"}

        while True:
            print(
                "Please note that this system only launches free tier AMIs in eu-west-1 region"
            )
            print("\nSelect AMI Type")
            print("1. Linux")
            print("2. Windows")
            print("3. Back to EC2 action Menu")
            choice = input("Enter your choice:").lower()

            if choice in launch_details:
                try:
                    image_id = launch_details[choice]
                    response = self.ec2_client.run_instances(
                        ImageId=image_id,
                        InstanceType="t3.micro",
                        MaxCount=1,
                        MinCount=1,
                    )

                    instance_id = response["Instances"][0]["InstanceId"]
                    print("The launched instance id is: ", instance_id)
                    return None
                except Exception as ex:
                    print(f"Error: Unable to launch instance due to - {ex}")

            elif choice == "3":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def terminate_instance(self):
        "Terminates a specified instance"
        while True:
            ("\nSelect an Instance ID")
            running_instance, stopped_instance = self.list_instanceId()
            print("")
            choice = input(
                "Enter your instance ID choice (or type 'exit' to go back to ec2 action menu): "
            )

            if running_instance or stopped_instance:
                self.terminate_instance_util(choice)
                return None
            elif choice == "exit":
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def list_all_instances(self):
        "A helper method that lists all instances within the aws account along with their details"

        print("\nFetching details about the instances in your account. Please wait....")
        region_running_instances = {}
        region_other_instances = {}

        regions = [
            region["RegionName"]
            for region in self.ec2_client.describe_regions()["Regions"]
        ]

        for region in regions:
            ec2_region_client = Client(
                self.access_key, self.secret_key, region
            ).ec2_client()
            response = ec2_region_client.describe_instances()
            running_instances, other_instances = categorize_ec2_response(response)

            if running_instances:
                region_running_instances[region] = running_instances
            if other_instances:
                region_other_instances[region] = other_instances

            region_running_instances[region] = running_instances
            region_other_instances[region] = other_instances

        print(
            "\n*****************************Running Instances*********************************"
        )
        for region, instances in region_running_instances.items():
            if instances:
                # print(f"Region: {region}")
                for instance in instances:
                    formatted_info = ", ".join(
                        [
                            f"{index}: {key}: {value}"
                            for index, (key, value) in enumerate(instance.items())
                        ]
                    )
                    print(formatted_info)

        print(
            "\n*****************************Other Instances************************************"
        )
        for region, instances in region_other_instances.items():
            if instances:
                # print(f"Region: {region}")
                for instance in instances:
                    formatted_info = ", ".join(
                        [
                            f"{index}: {key}: {value}"
                            for index, (key, value) in enumerate(instance.items())
                        ]
                    )
                    print(formatted_info)

        return None

    def list_region_instances(self):
        "A helper method that lists all instances within the region along with their details"

        print(
            f"\nFetching details about the instances in your region {self.region}. Please wait...."
        )
        response = self.ec2_client.describe_instances()
        running_instances, other_instances = categorize_ec2_response(response)

        if running_instances:
            print(
                "\n*****************************Running Instances*********************************"
            )
            for instance in running_instances:
                formatted_info = ", ".join(
                    [
                        f"{index}: {key}: {value}"
                        for index, (key, value) in enumerate(instance.items())
                    ]
                )
                print(formatted_info)

        elif other_instances:
            print(
                "\n*****************************Other Instances************************************"
            )
            for instance in other_instances:
                formatted_info = ", ".join(
                    [
                        f"{index}: {key}: {value}"
                        for index, (key, value) in enumerate(instance.items())
                    ]
                )
                print(formatted_info)
        else:
            print(f"No instance resides in {self.region} region")
        return None

    def list_instanceId(self):
        "A helper method that lists running and stopped instances as a list"
        running_instances = []
        stopped_instances = []
        try:
            response = self.ec2_client.describe_instances()
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    instance_state = instance["State"]["Name"]

                    if instance_state == "running":
                        running_instances.append(instance_id)
                    elif instance_state == "stopped":
                        stopped_instances.append(instance_id)

            print(f"Running Instances: {running_instances}")
            print(f"Stopped Instances: {stopped_instances}")
            return running_instances, stopped_instances
        except Exception as ex:
            print(f"Error: {ex}")

    def start_instance_util(self, instance_id):
        "A helper method for starting an EC2 instance"
        try:
            self.ec2_client.start_instances(InstanceIds=[instance_id])
            print(
                f"\nStarting the instance with ID {instance_id}. Please wait for it to become operational..."
            )
            waiter = self.ec2_client.get_waiter("instance_running")
            waiter.wait(InstanceIds=[instance_id])
            print(f"Instance with ID {instance_id} is running.")
        except Exception as ex:
            print("Error: Unable to start the instance:", ex)

    def stop_instance_util(self, instance_id):
        "A helper method for stopping an EC2 instance"
        try:
            self.ec2_client.stop_instances(InstanceIds=[instance_id])
            print(
                f"\nStopping the instance with ID {instance_id}. Please wait for it to come to a stop..."
            )
            waiter = self.ec2_client.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[instance_id])
            print(f"The instance {instance_id} has been successfully stopped.")
        except Exception as ex:
            print("Error: Unable to stop the instance:", ex)

    def terminate_instance_util(self, instance_id):
        "A helper function for terminating EC2 instance"
        try:
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            print(f"The instance {instance_id} has been terminated.")
        except Exception as ex:
            print("Error: Unable to terminate the instance:", ex)


def manage_ec2(access_key, secret_key, region):
    "Provides an interactive menu for managing EC2 instances"
    action = EC2Actions(access_key, secret_key, region)
    while True:
        print("\nSelect an EC2 action")
        print("1. List Instances")
        print("2. Start Instance")
        print("3. Stop Instance")
        print("4. Launch Instance")
        print("5. terminate Instance")
        print("6. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_instances()
        elif choice == "2":
            action.start_instance()
        elif choice == "3":
            action.stop_instance()
        elif choice == "4":
            action.launch_instance()
        elif choice == "5":
            action.terminate_instance()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please select a valid option.")
