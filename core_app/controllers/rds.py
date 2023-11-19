from interface import Client


class RDSActions:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.rds_client = Client(access_key, secret_key, region).rds_client()

    def list_rds_instances(self):
        "It lists all the rds instance in the user's logged in region"
        response = self.rds_client.describe_db_instances()
        for db_instance in response["DBInstances"]:
            print(
                f'Instance Identifier: {db_instance["DBInstanceIdentifier"]}, Status: {db_instance["DBInstanceStatus"]}'
            )

    def start_rds_instance(self):
        "It starts up an rds instance specified by the user"
        db_instance_identifier = input("Enter your db instance identifier: ").strip()

        try:
            response = self.rds_client.start_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            print(f"Starting RDS instance '{db_instance_identifier}'")
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            print(f"RDS instance '{db_instance_identifier}' not found")
        except self.rds_client.exceptions.InvalidDBInstanceStateFault:
            print(
                f"RDS instance '{db_instance_identifier}' is already in the 'available' state"
            )
        except Exception as ex:
            print(f"Error: Unable to start the rds instance due to - : {str(ex)}")

    def stop_rds_instance(self):
        "stops rds instance specified by the user "
        db_instance_identifier = input("Enter your db instance identifier: ").strip()

        try:
            response = self.rds_client.stop_db_instance(
                DBInstanceIdentifier=db_instance_identifier
            )
            print(f"Stopping RDS instance '{db_instance_identifier}'")
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            print(f"RDS instance '{db_instance_identifier}' not found")
        except self.rds_client.exceptions.InvalidDBInstanceStateFault:
            print(
                f"RDS instance '{db_instance_identifier}' is already in the 'stopped' state"
            )
        except Exception as ex:
            print(f"Error: Unable to stop the rds instance due to - : {str(ex)}")

    def delete_rds_instance(self):
        "deletes rds instance specified by the user"
        db_instance_identifier = input("Enter your db instance identifier: ").strip()
        response = self.rds_client.delete_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            SkipFinalSnapshot=True,  # Set to False to create a final DB snapshot before deletion
        )

        print(f"Deleting MySQL instance {db_instance_identifier}.")


def manage_rds(access_key, secret_key, region):
    "Provides an interactive menu for managing rds instances"
    action = RDSActions(access_key, secret_key, region)
    while True:
        print("\nSelect RDS action")
        print("1. List RDS Instances")
        print("2. Start RDS Instance")
        print("3. Stop RDS Instance")
        print("4. Delete RDS Instance")
        print("5. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_rds_instances()
        elif choice == "2":
            action.start_rds_instance()
        elif choice == "3":
            action.stop_rds_instance()
        elif choice == "4":
            action.delete_rds_instance()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select a valid option.")
