
import boto3
from auth import user_access

class Resource:

    def __init__(self, access_key, secret_key):

        # self.access_key, self.secret_key = user_access()
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = "eu-west-1"

    def ec2_resource(self):
        ec2 = boto3.resource("ec2",aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key,
                              region_name=self.region)
        return ec2
