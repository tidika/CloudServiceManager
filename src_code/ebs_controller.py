import string

from interface import Client
from ec2_controller import EC2Actions
from utils import confirm_choices


class EBSActions:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ec2_client = Client(access_key, secret_key, region).ec2_client()
        self.ec2_actions = EC2Actions(access_key, secret_key, region)

    def list_volume(self):
        "Lists all the ebs volume within an aws account"

        print(
            "\nFetching details about the ebs Volumes in your account. Please wait...."
        )
        volume_list = {}
        regions = [
            region["RegionName"]
            for region in self.ec2_client.describe_regions()["Regions"]
        ]
        for region in regions:
            region_volume_list = []
            ec2_region_client = Client(
                self.access_key, self.secret_key, region
            ).ec2_client()

            response = ec2_region_client.describe_volumes()

            volumes = response["Volumes"]
            if volumes:
                for volume in volumes:
                    region_volume_list.append(
                        {
                            "VolumeID": volume["VolumeId"],
                            "Size(GB)": volume["Size"],
                            "Availability Zone": volume["AvailabilityZone"],
                            "State": volume["State"],
                        }
                    )
                    volume_list[region] = region_volume_list
        for region, volumes in volume_list.items():
            print(f"\nRegion: {region}")
            for volume in volumes:
                print(volume)

    def create_volume(self):
        while True:
            while True:
                az_choice = input("Enter the AZ: ").lower()
                size_choice = input("Enter the volume size: ")
                voltype_choice = input("Enter the volume type: ").lower()

                confirm_choices()

                while True:
                    choice = input("Enter your choice:").lower()
                    if choice == "1":
                        try:
                            response = self.ec2_client.create_volume(
                                AvailabilityZone=az_choice,
                                Size=int(size_choice),
                                VolumeType=voltype_choice,
                            )
                            new_volume_id = response["VolumeId"]
                            print(
                                f"\nCreating a new volume with volume ID {new_volume_id}. Please wait for it to become operational..."
                            )

                            self.ec2_client.get_waiter("volume_available").wait(
                                VolumeIds=[new_volume_id],
                            )
                            print(f"New volume created with ID: {new_volume_id}")
                            return new_volume_id
                        except Exception as ex:
                            print(
                                "Error: Unable to create a volume due to this error - ",
                                ex,
                            )

                    elif choice == "2":
                        break

                    elif choice == "3":
                        return None
                    else:
                        print("Invalid choice. Please select a valid option.")

    def attach_volume(self):
        instance_id = input("Enter the EC2 Instance ID: ").lower()
        device = self.choose_unique_device_name(instance_id)

        # Identify what AZ the given instance ID belongs to
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            reservations = response["Reservations"]
            for reservation in reservations:
                instances = reservation["Instances"]
                for instance in instances:
                    az = instance["Placement"]["AvailabilityZone"]
        except Exception as ex:
            print(f"Error: {ex}")

        # Check if there are volumes that are not in use
        unused_vol = self.list_unused_volumes_by_az(az)
        if unused_vol:
            print(
                f"\nHere are the Available volumes that are unused in the AZ {az} where your specified instance {instance_id} is located"
            )
            for volume in unused_vol:
                print(volume)

            while True:
                volume_id_choice = input(
                    "\nEnter the volume you want to attach or 'exit' to go back to EBS action menu): "
                )
                self.attach_volume_utils(device, instance_id, volume_id_choice)
                return None
        else:
            print(
                f"\nThere is no available volume on the AZ {az} where the instance {instance_id} is located."
            )
            choice = input(
                "Would you like to create a volume to attach to the instance? (yes/no): "
            )
            if choice == "yes":
                new_volume_id = self.create_volume()
                print(
                    f"Attaching {new_volume_id} to instance with ID {instance_id} ... "
                )
                self.attach_volume_utils(device, instance_id, new_volume_id)
                return None
            else:
                return None

    def list_unused_volumes_by_az(self, az):
        try:
            response = self.ec2_client.describe_volumes(
                Filters=[{"Name": "availability-zone", "Values": [az]}]
            )
            volumes = response["Volumes"]
            unused_volume = []
            for volume in volumes:
                state = volume["State"]
                vol_id = volume["VolumeId"]
                az = volume["AvailabilityZone"]
                vol_size = volume["Size"]

                # Extracting device name from the Attachments field
                attachments = volume.get("Attachments", [])
                device_name = attachments[0]["Device"] if attachments else None

                if state == "available":
                    new_volume_details = {
                        "VolumeId": vol_id,
                        "State": state,
                        "AZ": az,
                        "Size": vol_size,
                        "DeviceName": device_name,
                    }
                    unused_volume.append(new_volume_details)
            return unused_volume
        except Exception as ex:
            print(f"Error: {ex}")

    def attach_volume_utils(self, device, instance_id, volume_id):
        try:
            self.ec2_client.attach_volume(
                Device=device, InstanceId=instance_id, VolumeId=volume_id
            )
            print(
                f"\nVolume {volume_id} attached to instance {instance_id} at device {device}"
            )
        except Exception as ex:
            print(f"Error: Unable to attach the volume due to - {ex}")

    def get_existing_device_names(self, instance_id):
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            existing_device_names = set()

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    for attachment in instance.get("BlockDeviceMappings", []):
                        device_name = attachment["DeviceName"]
                        existing_device_names.add(device_name)

            return existing_device_names

        except Exception as ex:
            print(f"Error: {ex}")
            return set()

    def choose_unique_device_name(self, instance_id):
        #TODO test this new functionality of being ablbe to attach a root volume. 
        choice = input("Do you want to attach a root volume? (yes/no): ")

        if choice == "no":
            existing_device_names = self.get_existing_device_names(instance_id)
            available_letters = set(
                string.ascii_lowercase[5:15]
            )  # [f-p] which is aws range for device storage being mounted.

            for letter in available_letters:
                potential_device_name = f"/dev/sd{letter}"

                if potential_device_name not in existing_device_names:
                    return potential_device_name

            print("Error: No available device names.")
            return None
        else: 
            potential_device_name = "dev/xvda"
            return potential_device_name

    def detach_vol_utils(self, instance_id, volume_id_choice):
        try:
            self.ec2_client.detach_volume(
                InstanceId=instance_id, VolumeId=volume_id_choice
            )
            print(
                f"\nDetaching volume with volume ID {volume_id_choice} from instance with instance ID {instance_id}. Please wait for the device to become fully detached..."
            )

            waiter = self.ec2_client.get_waiter("volume_available")
            waiter.wait(VolumeIds=[volume_id_choice])

            print(f"Volume {volume_id_choice} is now detached and available for use")
        except Exception as ex:
            print(f"Error: Unable to detach the volume due to - {ex}")

    def detach_volume(self):
        instance_id = input("Enter the EC2 Instance ID: ").lower()
        vol_id = {"root_device": [], "non_root_device": []}
        volume_detail_list = []

        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            print(
                "\n************************** The volumes attached to this instance are: ****************************"
            )
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    state = instance["State"]["Name"]

                    for block_device in instance["BlockDeviceMappings"]:
                        delete_on_termination = block_device["Ebs"][
                            "DeleteOnTermination"
                        ]
                        vol_type = (
                            "Root device"
                            if delete_on_termination
                            else "Non-root device"
                        )
                        vol_id[
                            "root_device"
                            if delete_on_termination
                            else "non_root_device"
                        ] = block_device["Ebs"]["VolumeId"]
                        volume_detail = {
                            "Device Name": block_device["DeviceName"],
                            "Volume ID": block_device["Ebs"]["VolumeId"],
                            "Root device?": vol_type,
                        }
                        volume_detail_list.append(volume_detail)

            for volume in volume_detail_list:
                print(volume)

        except Exception as ex:
            print(f"Error: {ex}")
            return

        print("\nSelect Volume ID to detach based on the available options above: ")
        while True:
            volume_id_choice = input(
                "Enter the Volume ID (or 'exit' to go back to EBS action menu): "
            ).lower()
            if volume_id_choice in vol_id["non_root_device"]:
                self.detach_vol_utils(instance_id, volume_id_choice)
                return None
            elif volume_id_choice in vol_id["root_device"]:
                if state == "running":
                    self.ec2_actions.stop_instance_util(instance_id)
                self.detach_vol_utils(instance_id, volume_id_choice)
                return None
            else:
                print("Invalid choice... please select a valid Volume ID")

    def modify_volume(self):
        print(
            "To decrease a volume size,take a snapshot and then create a volume out of the snapshot"
        )
        volume_id_choice = input("Enter the volume ID: ")
        volume_size_choice = input("Enter the volume target size: ")
        response = self.ec2_client.describe_volumes(VolumeIds=[volume_id_choice])
        original_size = response["Volumes"][0]["Size"]

        if int(volume_size_choice) > original_size:
            try:
                response = self.ec2_client.modify_volume(
                    VolumeId=volume_id_choice, Size=int(volume_size_choice)
                )

                print(response)

                modified_volume_id = response["VolumeModification"]["VolumeId"]
                print(
                    f"Volume {modified_volume_id} is being modified. Waiting for it to be available..."
                )

                waiter = self.ec2_client.get_waiter("volume_available")
                waiter.wait(VolumeIds=[modified_volume_id])
                print(
                    f"Volume {modified_volume_id} has been successfully modified and is now available."
                )
                return modified_volume_id
            except Exception as ex:
                print(f"Error: Unable to modify the volume due to - {ex}")

        else:
            print(
                "\nThe target volume size is smaller than the orginal size. So, taking a snapshot and then creating a new volume."
            )

            # create a snapshot
            print("\nCreating a snapshot ...")
            try:
                response = self.ec2_client.create_snapshot(
                    VolumeId=volume_id_choice,
                    Description=f"Saving a volume with ID {volume_id_choice} so I can create a new volume with the target size",
                )
                snapshot_id = response["SnapshotId"]
                print(f"Snapshot with the ID: {snapshot_id} has being created.")
            except Exception as ex:
                print("Error: Unable to take snapshot due to - {ex}")

            # create volume with target size
            print("Creating volume with target size ...")
            vol_type_choice = input("Enter the volume type (default is gp2): ")
            try:
                response = self.ec2_client.describe_volumes(
                    VolumeIds=[volume_id_choice]
                )
                az = response["Volumes"][0]["AvailabilityZone"]
            except Exception as ex:
                print(f"Error: Unable to get volume information due to - {ex}")

            if not vol_type_choice.strip():
                vol_type_choice = "gp2"

            response = self.ec2_client.create_volume(
                AvailabilityZone=az,
                Size=int(volume_size_choice),
                VolumeType=vol_type_choice,
            )
            target_volume_id = response["VolumeId"]
            print(f"Target Volume with the ID: {target_volume_id} has being created.")

            delete_choice = input(
                "Would you like me to delete the original volume (yes or no): "
            ).lower()
            if delete_choice == "yes":
                # delete the original volume
                print("deleting the original volume")
                self.ec2_client.delete_volume(VolumeId=volume_id_choice)
                print(f"Volume {volume_id_choice} deleted successfully.")

    def list_snapshots(self):
        snapshot_list = []
        try:
            response = self.ec2_client.describe_snapshots(OwnerIds=["self"])
            print(response)
            snapshots = response["Snapshots"]

            if snapshots:
                for snapshot in snapshots:
                    snapshot_dict = {
                        "Snapshot ID": snapshot["SnapshotId"],
                        "Volume ID": snapshot["VolumeId"],
                        "Start Time": snapshot["StartTime"],
                        "State": snapshot["State"],
                        "VolumeSize": snapshot["VolumeSize"],
                    }
                    snapshot_list.append(snapshot_dict)
            else:
                print("\nNo snapshots available.....")
        except Exception as ex:
            print(f"Error: Encountered an error while listing snapshot due to - {ex}")

        for snapshot in snapshot_list:
            formatted_info = ", ".join(
                [
                    f"{index}: {key}: {value}"
                    for index, (key, value) in enumerate(snapshot.items())
                ]
            )
            print(formatted_info)

    def take_snapshots(self):
        volume_id_choice = input("Enter the volume ID: ")

        try:
            response = self.ec2_client.create_snapshot(
                VolumeId=volume_id_choice,
                Description=f"Taking a snapshot from a volume with ID {volume_id_choice}",
            )
            snapshot_id = response["SnapshotId"]
            print(
                f"Snapshot with the ID: {snapshot_id} has been created from Volume ID {volume_id_choice}."
            )
        except Exception as ex:
            print("Error: Unable to take snapshot due to - {ex}")

    def create_vol_from_snapshot(self):
        snapshot_id = input("Enter the snapshot ID: ")

        # get the volume id that created the snapshot
        try:
            response = self.ec2_client.describe_snapshots(SnapshotIds=[snapshot_id])
            vol_id = response["Snapshots"][0]["VolumeId"]
        except Exception as ex:
            print(f"Error: Unable to get snapshot information due to - {ex}")

        # get the az where the volume that created the snapshot belong to.
        try:
            response = self.ec2_client.describe_volumes(VolumeIds=[vol_id])
            az = response["Volumes"][0]["AvailabilityZone"]
        except Exception as ex:
            print(f"Error: Unable to get volume information due to - {ex}")

        print("\nPlease provide the parameters for the volume to be created. ")
        print(
            f"NOTE: The Availability Zone (AZ) of the original volume that created the snapshot is {az}."
        )

        self.create_volume()


def manage_ebs(access_key, secret_key, region):
    action = EBSActions(access_key, secret_key, region)
    while True:
        print("\nSelect EBS action")
        print("1. List Volumes")
        print("2. Create Volume")
        print("3. Attach Volume")
        print("4. Detach Volume")
        print("5. Modify Volume")
        print("6. List Snapshot")
        print("7. Take snapshot")
        print("8. Create Volume From Snapshot")
        print("9. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_volume()
        elif choice == "2":
            action.create_volume()
        elif choice == "3":
            action.attach_volume()
        elif choice == "4":
            action.detach_volume()
        elif choice == "5":
            action.modify_volume()
        elif choice == "6":
            action.list_snapshots()
        elif choice == "7":
            action.take_snapshots()
        elif choice == "8":
            action.create_vol_from_snapshot()
        elif choice == "9":
            break
        else:
            print("Invalid choice. Please select a valid option.")


# if __name__ == "__main__":
#     manage_ebs()
