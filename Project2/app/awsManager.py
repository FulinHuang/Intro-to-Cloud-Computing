import boto3
from app import config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta


class Manager:

    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')
        self.cloudwatch = boto3.client('cloudwatch')


    # Get CPU utilization of the worker in past 30 min from cloudwatch
    def inst_CPU(self, inst_id):
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(inst_id)  # Identify the instance by ID

        start = 31
        end = 30  # the fist time interval is 31 to 30
        CPU_utl = []  # A list to store CPU utilization in past 30 min
        for times in range(0, 30):
            CPU = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance.id
                    },
                ],
                StartTime=datetime.utcnow() - timedelta(seconds=start * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=end * 60),
                Period=30,  # Every 60 sec get once data
                Statistics=['Average']
            )
            print('***CPU info:', CPU)
            # Time interval shifts by 1 min
            start -= 1
            end -= 1
            utilization = 0  # Initialize utilization of each 1 min
            for data in CPU['Datapoints']:
                print('***Datapoints:', data)
                utilization = round(data['Average'], 2)  # Round off the float, keep 2 digits
            CPU_utl.append(utilization)  # Contain 30 CPU utilzations values

        x_axis = list(range(1, 31))
        return x_axis, CPU_utl


    def avg_cpu(self, instances):
        cpu = []
        for instance in instances:

            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance.id
                    },
                ],
                StartTime=datetime.utcnow(),
                EndTime=datetime.utcnow() - timedelta(seconds=120),
                Period=60,
                Statistics=['Average']
            )

            for data in response['Datapoints']:
                data_avg = data['Average']
                cpu.append(data_avg)

        avg_cpu = sum(cpu) / len(cpu)
        return avg_cpu


    # Get HTTP request rate of the worker in past 30 min
    def inst_HTTP(self, inst_id):
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(inst_id)
        watch = boto3.client('cloudwatch')
        start = 31
        end = 30  # fist time interval is 31 to 30
        http_rate = []  # A list to store HTTP request rate in past 30 min
        for times in range(0, 30):
            HTTP = watch.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='RequestCountPerTarget',
                Dimensions=[
                    {
                        'Name': 'TargetGroup',
                        'Value': config.target_group_dimension
                    },
                ],
                StartTime=datetime.utcnow() - timedelta(seconds=start * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=end * 60),
                Period=30,
                Statistics=['Sum']
            )
            print('**HTTP info:', HTTP)
            start -= 1
            end -= 1
            http_count = 0  # Initialize HTTP request of each 1 min
            for data in HTTP['Datapoints']:
                http_count = int(data['Sum'])  # Save the count number as an integer
            http_rate.append(http_count)

            x_axis = list(range(1, 31))
        return x_axis, http_rate
    

    # Count the number of workers in past 30 minutes
    def number_workers(self):
        ec2 = boto3.resource('ec2')
        watch = boto3.client('cloudwatch')

        start = 31
        end = 30  # fist time interval is 31 to 30
        inst_num = []  # A list to store number of workers in past 30 min

        for times in range(0, 30):
            NUM_INSTANCES = watch.get_metric_statistics(
                Namespace='AWS/ApplicationELB',
                MetricName='HealthyHostCount',
                Dimensions=[
                    {
                        'Name': 'TargetGroup',
                        'Value': config.target_group_dimension
                    },
                    {
                        'Name': 'LoadBalancer',
                        'Value': config.ELB_dimension
                    }
                ],
                StartTime=datetime.utcnow() - timedelta(seconds=start * 60),
                EndTime=datetime.utcnow() - timedelta(seconds=end * 60),
                Period=60,
                Statistics=['Average']
            )

            for data in NUM_INSTANCES['Datapoints']:
                inst_count = int(data['Average'])  # Save the count number as an integer
                inst_num.append(inst_count)

            start -= 1
            end -= 1

        x_axis = list(range(0, len(inst_num)))

        return x_axis, inst_num
    

    # Create a ec2 instance
    def create_new_instance(self):
        try:
            new_instance = self.ec2.run_instances(
                ImageId = config.ImageId,
                MinCount = 1,
                MaxCount = 1,
                InstanceType = 't2.large',
                KeyName = config.KeyName,
                Monitoring = {'Enable': True},
                TagSpecialications = config.tag_specificatios,
                Placement = config.placement,
                SecurityGroups = config.security_group,
                IamInstanceProfile = config.iam_instance_profile,
                UserData = config.user_data

            )
            new_instance = new_instance[0]

            # Wait for state to change before register it to a target group
            new_instance.wait_until_running(
                Filters=[
                    {
                        'Name': 'instance-id',
                        'Values': [new_instance.id]
                    }
                ]
            )
            new_instance.reload()

            # Register to a target group
            response = self.register_to_target_group(new_instance)
            print(response)


            return new_instance

        except ClientError as e:
            print(e)



    # Get all user instances
    # State could be : running, pending, stopped, etd ...
    def get_user_instances(self, state):
        instance_list = []
        # Look for all user instances that satisfy the conditions
        instances = self.ec2.describe_instances(
            Filters=[{'Name': 'tag:Name',
                      'Values': [config.user_tag]
                      },
                     {
                         'Name': 'instance-state-name',
                         'Values': [state]
                     },
                     {'Name': 'image-id',
                      'Values': [config.ImageId]}
                     ]
        )
        for instance in instances:
            instance_list.append(instance)

        return instance_list


    # Register an ec2 instance to destinated target group
    def register_to_target_group(self, instance):
        response = self.elb.register_targets(
            TargetGroupArn=config.target_arn,
            Targets= {
                'Id': instance.id
            })

        # check response
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Successfully registered targets! Code - 200")

            return response['ResponseMetadata']['HTTPStatusCode']
        else:
            print("Register targets failed!")
            return -1



    def remove_instance(self, instanceId):
        response = self.elb.deregister_targets(
            TargetGroupArn=config.target_arn,
            Targets=[
                {
                    'Id': instanceId,
                },
            ]
        )
        print(response)

        # Unregister an instance from the target group

        self.unregister_from_target_group(instanceId)

        # Terminate instance by instanceId
        self.ec2.instances.filter(InstanceIds=instanceId).terminate()
        print("Instance i " + instanceId + " is terminated")
        # TODO:  catch exception


    # Unregister an instance from the target group
    def unregister_from_target_group(self, instanceId):

        # Wait for deregister
        waiter = self.elb.get_waiter('target_deregistered')
        waiter.wait(
            TargetGroupArn = config.target_arn,
            Targets = [
                {
                    'Id': instanceId
                },
            ],
            WaiterConfig={
                'Delay': 15,
                'MaxAttempts': 40
            }
        )
        print("Instance id " + instanceId + " is deregistered")


    def get_healthy_ids(self):
        running_ids = []
        healthy_ids = []

        # Get user running instances
        running_instances = self.get_user_instances('running')
        for instance in running_instances:
            running_ids.append(instance.id)

        for instanceId in running_ids:
            response = self.elb.describe_target_health(
                TargetGroupArn=config.target_arn,
                Targets=[
                    {
                        'Id': instanceId,
                        'Port': 5000
                    }
                ]
            )
            if response['TargetHealthDescriptions'][0]['TargetHealth']['State'] == 'healthy':
                healthy_ids.append(instanceId)

        return healthy_ids


    # Increase worker based on ratio
    def increase_worker(self, ratio, num_instance, max_instance):
        num_increase = int(num_instance * ratio - num_instance)
        if num_increase < 0:
            num_increase = 0

        if num_increase + num_instance > max_instance:
            num_increase = max_instance - num_instance

        for i in range(num_increase):
            self.create_new_instance()


    # Decrase worker by ratio
    def decrease_worker(self, ratio, instance_ids, num_instance, min_instance):
        num_decrease = int(num_instance - num_instance * ratio)
        if num_decrease < 0:
            num_decrease = 0

        if num_instance - num_decrease < min_instance:
            num_decrease = num_instance - min_instance

        remove_id = instance_ids[:num_decrease]
        for id in remove_id:
            self.remove_instance(id)



