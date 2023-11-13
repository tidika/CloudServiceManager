from interface import Client

class RDSActions:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.rds_client = Client(access_key, secret_key, region).rds_client()

    def create_rds_instance(self):
        pass

    def list_rds_instances(self):
        pass

    def modify_rds_instance(self):
        pass

    def delete_rds_instance(self):
        pass


def manage_rds(access_key, secret_key, region):
    action = RDSActions(access_key, secret_key, region)
    while True:
        print("\nSelect RDS action")
        print("1. Create RDS Instance")
        print("2. List RDS Instances")
        print("3. Modify RDS Instance")
        print("4. Delete RDS Instance")
        print("5. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.create_rds_instance()
        elif choice == "2":
            action.list_rds_instances()
        elif choice == "3":
            action.modify_rds_instance()
        elif choice == "4":
            action.delete_rds_instance()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select a valid option.")