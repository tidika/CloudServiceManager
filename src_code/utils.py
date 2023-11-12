
def categorize_ec2_response(response):
    running_instances = []
    other_instances = []

    # Process the instances
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # Extract instance details
            state = instance["State"]["Name"]
            ami_id = instance["ImageId"]
            instance_type = instance["InstanceType"]
            region = instance["Placement"]["AvailabilityZone"][:-1]
            launch_time = instance["LaunchTime"]
            instance_id = instance["InstanceId"]

            # Format launch_time as a string
            if state == "running":
                launch_time_str = launch_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                launch_time_str = "N/A"

            # Store instance information in the appropriate list
            if state == "running":
                running_instances.append(
                    {   
                        "Instance ID":instance_id,
                        "State": state,
                        "AMI ID": ami_id,
                        "Instance Type": instance_type,
                        "Region": region,
                        "Launch Time": launch_time_str,
                    }
                )
            else:
                other_instances.append(
                    {
                        "State": state,
                        "AMI ID": ami_id,
                        "Instance Type": instance_type,
                        "Region": region,
                        "Launch Time": launch_time_str,
                    }
                )

    return running_instances, other_instances

def confirm_choices():
    print("\nDo you Confirm your choices?")
    print("1. Yes to confirm")
    print("2. Retry to re-enter new parameter values")
    print("3. Back to EBS action Menu")

# def show_instances():
#     print("\nSelect an Instance ID")
#     print("1. i-03aeb95ee2eb5d041")
#     print("2. i-06fc919515f7a6260")
#     print("3. Back to EC2 actions Menu")


