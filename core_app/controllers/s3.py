import os
from interface import Client


class S3Actions:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.s3_client = Client(access_key, secret_key, region).s3_client()

    def list_bucket(self):
        "It lists all the bucket in the users AWS account"
        try:
            response = self.s3_client.list_buckets()
            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]
                region = self.s3_client.head_bucket(Bucket=bucket_name)[
                    "ResponseMetadata"
                ]["HTTPHeaders"]["x-amz-bucket-region"]
                print(f"Bucket Name: {bucket_name}, Region: {region}")
        except Exception as ex:
            print(
                "Error: Unable to list buckets in the account due to this error - ", ex
            )

    def list_bucket_objects(self):
        "It lists all object within the bucket provided by the user"
        bucket_name_choice = input(
            "Enter your bucket name: "
        ).strip()  # to remove leading and trailing spaces
        print(f"\nThe available objects within {bucket_name_choice} bucket are: ")

        try:
            response = self.s3_client.list_objects(Bucket=bucket_name_choice)
            for obj in response.get("Contents", []):
                print(f'Object Key: {obj["Key"]}')
            return bucket_name_choice
        except Exception as ex:
            print("Error: Unable to list buckets objects due to this error - ", ex)

    def project_root(self):
        "it gets the core_app directory"
        script_path = os.path.abspath(__file__)
        project_root = os.path.dirname(
            os.path.dirname(script_path)
        )  # get the project root directory.
        return project_root

    def upload_object(self):
        "Uploads data to an S3 bucket specified by the user"
        bucket_name_choice = input("Enter your bucket name: ").strip()
        filename_choice = input(
            "Enter the file name to upload (file Must be located in the 'data' folder): "
        ).strip()
        print(filename_choice)
        try:
            project_root = self.project_root()
            print(project_root)
            local_file_path = os.path.join(
                project_root, "data", "uploads", filename_choice
            )
            self.s3_client.upload_file(
                local_file_path, bucket_name_choice, filename_choice
            )
            print(
                f" The {filename_choice} file has been uploaded to {bucket_name_choice} bucket"
            )
        except Exception as ex:
            print("Error: Unable to upload the object due to this error - ", ex)

    def download_object(self):
        bucket_name_choice = self.list_bucket_objects()
        object_choice = input(
            "Enter the object path (file or folder) to download: "
        ).strip()

        try:
            project_root = self.project_root()
            local_file_path = os.path.join(
                project_root, "data", "downloads", object_choice
            )

            # Check if the object is a folder by listing its contents
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name_choice,
                Prefix=object_choice,
                MaxKeys=1,  # MaxKeys=1 means we're only checking if there's something
            )

            if "Contents" in response:
                # Object is a folder, recursively download all its contents
                for obj in response["Contents"]:
                    key = obj["Key"]
                    file_name = key.split("/")[-1]  # Extract file name
                    local_file_path = os.path.join(
                        project_root, "data", "downloads", file_name
                    )
                    self.s3_client.download_file(
                        bucket_name_choice, key, local_file_path
                    )
                print(
                    f"The folder {object_choice} has been downloaded to data/downloads."
                )
            else:
                # Object is a single file
                self.s3_client.download_file(
                    bucket_name_choice, object_choice, local_file_path
                )
                print(
                    f"The file {object_choice} has been downloaded to data/downloads."
                )

        except Exception as ex:
            print("Error: Unable to download the object due to this error - ", ex)

    def delete_bucket(self):
        "It deletes a bucket specified by the user"
        bucket_name_choice = input("Enter your bucketname: ").strip()
        try:
            response = self.s3_client.list_objects(Bucket=bucket_name_choice)
            if "Contents" in response:
                confirmation = input(
                    f"The bucket {bucket_name_choice} contains objects. Are you sure you want to delete it? (yes/no): "
                ).lower()
                if confirmation == "yes":
                    for obj in response["Contents"]:
                        self.s3_client.delete_object(
                            Bucket=bucket_name_choice, Key=obj["Key"]
                        )
                    self.s3_client.delete_bucket(Bucket=bucket_name_choice)
                    print(f"The bucket {bucket_name_choice} has been deleted")
                elif confirmation == "no":
                    print(
                        f"The bucket {bucket_name_choice} won't be deleted since it still has contents in it."
                    )
                else:
                    print("Invalid choice. Please select a valid option.")
            else:
                self.s3_client.delete_bucket(
                    Bucket=bucket_name_choice
                )  # deletes the empty bucket
                print(f"The bucket {bucket_name_choice} has been deleted")

        except Exception as ex:
            print(
                f"Error: Unable to delete the {bucket_name_choice} bucket due to this error - ",
                ex,
            )


def manage_s3(access_key, secret_key, region):
    "Provides an interactive menu for managing S3 bucket"
    action = S3Actions(access_key, secret_key, region)
    while True:
        print("\nSelect S3 action")
        print("1. List Bucket")
        print("2. List Bucket Objects")
        print("3. Upload Object")
        print("4. Download Object")
        print("5. Delete Bucket")
        print("6. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_bucket()
        elif choice == "2":
            action.list_bucket_objects()
        elif choice == "3":
            action.upload_object()
        elif choice == "4":
            action.download_object()
        elif choice == "5":
            action.delete_bucket()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please select a valid option.")
