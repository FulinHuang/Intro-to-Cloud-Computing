import boto3
from app import config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import time

class Manager:

    def __init__(self):
        self.ec2 = boto3.resource('ec2')
        self.elb = boto3.client('elbv2')
        self.cloudwatch = boto3.client('cloudwatch')
        self.s3 = boto3.resource('s3')

    # Calculate CPU utilization for all workers in past 30 min
    def inst_CPU(self, inst_id):
        instance = self.ec2.Instance(inst_id)  # Identify the instance by ID

        CPU_utl = []
        time_stamps = []
        time_point = datetime.utcnow()
        time_period = 30
        CPU = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance.id
                },
            ],
            StartTime=time_point - timedelta(seconds=time_period * 60),
            EndTime=time_point,
            Period=60,
            Statistics=['Average']
        )
        # sort the data points in timely order.
        all_points = sorted(CPU['Datapoints'], key=lambda k: k.get('Timestamp'), reverse=False)

        # Save the count number into inst_num as an integer
        for data_point in all_points:
            CPU_utl.append(round(data_point['Average'], 2))
            time_stamps.append(data_point['Timestamp']-timedelta(hours=4))

        return time_stamps, CPU_utl


    # Calcuate avg cpu for all workers over past 2 minutes
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
                StartTime=datetime.utcnow() - timedelta(seconds=120),
                EndTime=datetime.utcnow(),
                Period=60,
                Statistics=['Average']
            )

            for data in response['Datapoints']:
                data_avg = data['Average']
                cpu.append(data_avg)

        # In case cpu length is 0
        if len(cpu) == 0:
            avg_cpu = sum(cpu)
        else:
            avg_cpu = sum(cpu) / len(cpu)

        return avg_cpu

    # Calculate HTTP request rate for all workers in past 30 min
    def inst_HTTP(self, inst_id):
        ec2 = boto3.resource('ec2')
        time_point = datetime.utcnow()
        time_period = 30

        http_rate = []
        time_stamps = []

        HTTP = self.cloudwatch.get_metric_statistics(
            Namespace='Custom',
            MetricName='HTTP_COUNT_5000',
            Dimensions=[
                {
                    'Name': 'Instance',
                    'Value': inst_id
                },
            ],
            StartTime=datetime.utcnow() - timedelta(seconds=time_period * 60),
            EndTime=time_point,
            Period=60,
            Statistics=['Maximum']
        )

        all_points = sorted(HTTP['Datapoints'], key=lambda k: k.get('Timestamp'), reverse=False)

        for data_point in all_points:
            http_rate.append(int(data_point['Maximum']))
            time_stamps.append(data_point['Timestamp']-timedelta(hours=4))

        #x_axis = list(range(0, len(http_rate)))

        return time_stamps, http_rate

    # Calculate the number of workers in past 30 minutes
    def number_workers(self):
        time_point = datetime.utcnow()
        time_period = 30
        inst_num = []
        time_stamps = []

        inst_number = self.cloudwatch.get_metric_statistics(
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
            StartTime=time_point - timedelta(seconds=time_period * 60),
            EndTime=time_point,
            Period=60,
            Statistics=['Average'],
            )
        # sort the data points in timely order.
        all_points = sorted(inst_number['Datapoints'], key=lambda k: k.get('Timestamp'), reverse=False)
        # Save the count number into inst_num as an integer
        for data_point in all_points:
            inst_num.append(int(data_point['Average']))
            time_stamps.append(data_point['Timestamp']-timedelta(hours=4))

        return time_stamps, inst_num

    # Create a ec2 instance
    def create_new_instance(self):
        try:

            response = self.ec2.create_instances(
                ImageId=config.ImageId,
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.large',
                KeyName=config.KeyName,
                Monitoring={'Enabled': True},
                TagSpecifications=config.tag_specifications,
                Placement=config.placement,
                SecurityGroups=[config.security_group],
                IamInstanceProfile=config.iam_instance_profile,
                UserData=config.user_data

            )
            new_instance = response[0]

            print(datetime.now(),' Adding new instance ', new_instance, '...')
            # Wait for state to change before register it to a target group
            new_instance.wait_until_running(
                Filters=[
                    {
                        'Name': 'instance-id',
                        'Values': [new_instance.id]
                    }
                ]
            )
            print(datetime.now(), " wait until running...")
            new_instance.reload()

            # Register to a target group
            response = self.register_to_target_group(new_instance)
            print(datetime.now(), " registered to a target group :", response)

            instances = self.get_user_instances("running")
            instance_id = []
            for instance in instances:
                instance_id.append(instance.id)
            print(datetime.now(), ' Our worker pool has', len(instance_id), "instances running currently.")

            return new_instance

        except ClientError as e:
            print(e)

    # Get all user instances
    # State could be : running, pending, stopped, etd ...
    def get_user_instances(self, state):
        # Look for all user instances that satisfy the conditions
        responses = self.ec2.instances.filter(
            Filters=[{'Name': 'placement-group-name',
                      'Values': [config.user_placement] # worker group
                      },
                     {
                         'Name': 'instance-state-name',
                         'Values': [state]
                     },
                     {'Name': 'image-id',
                      'Values': [config.ImageId]}
                     ]
        )
        return responses

    # Register an ec2 instance to destinated target group
    def register_to_target_group(self, instance):
        response = self.elb.register_targets(
            TargetGroupArn=config.target_arn,
            Targets=[{
                'Id': instance.id
            }])

        # check response
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(datetime.now(), " Successfully registered targets! Code - 200")

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

        print(datetime.now(), " Removing an instance")

        # Unregister an instance from the target group
        self.unregister_from_target_group(instanceId)

        # Terminate instance by instanceId
        self.ec2.instances.filter(InstanceIds=[instanceId]).terminate()
        print(datetime.now(), " Instance i " + instanceId + " is terminated")

        time.sleep(20)

        instances = self.get_user_instances("running")
        instance_id = []
        for instance in instances:
            instance_id.append(instance.id)
        print(datetime.now(), ' Our worker pool has', len(instance_id), "instances running currently")

    # Unregister an instance from the target group
    def unregister_from_target_group(self, instanceId):

        # Wait for deregister
        waiter = self.elb.get_waiter('target_deregistered')
        waiter.wait(
            TargetGroupArn=config.target_arn,
            Targets=[
                {
                    'Id': instanceId
                },
            ],
            WaiterConfig={
                'Delay': 15,
                'MaxAttempts': 40
            }
        )

        print(datetime.now(), " Instance id " + instanceId + " is deregistered")

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

        return healthy_ids, running_ids

    def valid_for_autoscale(self):
        healthy_ids, running_ids  = self.get_healthy_ids()
        pending_ids = []
        stopping_ids = []
        pending_instances = self.get_user_instances('pending')
        stopping_instances = self.get_user_instances('stopping')

        for instance in pending_instances:
            pending_ids.append(instance)

        for instance in stopping_instances:
            stopping_ids.append(instance)

        if len(pending_ids) > 0 or len(stopping_ids) > 0:
            print(datetime.now(), " There are more than one pending/stopping instance")
            return False
        elif len(healthy_ids) != len(running_ids):
            print(datetime.now(), " # Healthy instances not equal to # running instances")
            return False
        else:
            return True


    # Increase worker based on ratio
    def increase_worker(self, ratio, num_instance, max_instance):
        num_increase = int(num_instance * ratio - num_instance)
        if num_increase < 0:
            num_increase = 0

        if num_increase + num_instance > max_instance:
            num_increase = max_instance - num_instance

        print(datetime.now(), " increase {} workers".format(num_increase))
        for i in range(num_increase):
            self.create_new_instance()

    # Decrase worker by ratio
    def decrease_worker(self, ratio, instance_ids, num_instance, min_instance):
        num_decrease = int(num_instance - num_instance * ratio)
        if num_decrease < 0:
            print("Cannot decrease worker")
            return

        if num_instance - num_decrease < min_instance:
            num_decrease = num_instance - min_instance

        remove_id = instance_ids[:num_decrease]

        print(datetime.now(), " Remove {} workers".format(len(remove_id)))

        for id in remove_id:
            self.remove_instance(id)


    def terminate_all(self):
        # Stop all workers
        instances = self.get_user_instances('running')
        inst_id = []
        for instance in instances:
            inst_id.append(instance.id)
        print(datetime.now(), " Currently there are ", len(inst_id), " running instances")

        for id in inst_id:
            print("We are removing instance", id, "...")
            self.remove_instance(id)
            print('This worker instance: {} has been removed successfully.'.format(id))

        # Stop manager
        manager_instance = self.ec2.instances.filter(InstanceIds=[config.manager_instance])
        manager_instance.stop()
        print(datetime.now(), " Manager is stopped")




