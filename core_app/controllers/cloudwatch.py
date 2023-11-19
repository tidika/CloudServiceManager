from datetime import datetime, timedelta
from interface import Client


class CloudWatchActions:
    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.cloudwatch_client = Client(
            access_key, secret_key, region
        ).cloudwatch_client()

    def display_metric_values(self):
        "Displays DiskReadOps, CPUCreditsUsage and DiskWriteBytes for an EC2 instance specified by the user"

        instance_id = input("Enter the EC2 instance ID: ")

        metrics = [
            {"MetricName": "DiskReadOps", "Unit": "Count"},
            {"MetricName": "CPUCreditUsage", "Unit": "Count"},
            {"MetricName": "DiskWriteBytes", "Unit": "Bytes"},
        ]
        dimensions = [{"Name": "InstanceId", "Value": instance_id}]

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)

        for metric in metrics:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName=metric["MetricName"],
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=["Average"],
            )

            datapoints = response["Datapoints"]
            if datapoints:
                average_value = datapoints[0]["Average"]
                print(
                    f'Average {metric["MetricName"]} over the last 30 minutes: {average_value}'
                )
            else:
                print(
                    f"No {metric['MetricName']} metric data is available for the {instance_id} instance in the last 30 minutes."
                )

    def set_alarm(self):
        "It sets alarm for DiskWriteBytes metric"

        alarm_name = "DiskWriteBytesAlarm"
        metric_name = "DiskWriteBytes"
        threshold = 9000

        instance_id = input("Enter the EC2 instance ID: ")
        dimensions = [{"Name": "InstanceId", "Value": instance_id}]

        self.cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            EvaluationPeriods=1,
            MetricName=metric_name,
            Namespace="AWS/EC2",
            Period=300,
            Statistic="Sum",
            Threshold=threshold,
            ActionsEnabled=True,
            AlarmActions=[f"arn:aws:automate:{self.region}:ec2:stop"],
            Dimensions=dimensions,
            Unit="Bytes",
        )

        print(
            f'Alarm "{alarm_name}" set for {metric_name} greater than or equal to {threshold} Bytes.'
        )


def manage_cloudwatch(access_key, secret_key, region):
    "Provides an interactive menu for managing cloudwatch"
    action = CloudWatchActions(access_key, secret_key, region)
    while True:
        print("\nSelect CloudWatch action")
        print("1. Display Metric Values")
        print("2. Set Alarm")
        print("3. Back to Services Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            action.display_metric_values()
        elif choice == "2":
            action.set_alarm()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select a valid option.")
