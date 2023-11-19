
from interface import Client


class AnsibleHosts:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.ec2_client = Client(access_key, secret_key, region).ec2_client()

    def provision_ec2_instances(self):
        pass
