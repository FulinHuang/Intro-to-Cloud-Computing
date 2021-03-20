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

    # Get CPU utilization of the worker in past 30 min from cloudwatch
    def inst_CPU(self, inst_id):

        # print('awsManager: loading the cpu utilization history of {}.'.format(inst_id))
        instance = self.ec2.Instance(inst_id)  # Identify the instance by ID

        CPU_utl = []  # A list to store CPU utilization in past 30 min
        time_point = datetime.utcnow()
        time_period = 30 # 30 minutes
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
            Period=60,  # Every 60 sec get once data
            Statistics=['Average']
        )
        for data_point in CPU['Datapoints']:
            CPU_utl.append(round(data_point['Average'], 2))
        x_axis = list(range(0, len(CPU_utl)))
        print(len(x_axis))
        # print('awsManager: the cpu utilization history is complete.')
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
                StartTime=datetime.utcnow() - timedelta(seconds=120),
                EndTime=datetime.utcnow(),
                Period=60,
                Statistics=['Average']
            )

            for data in response['Datapoints']:
                data_avg = data['Average']
                cpu.append(data_avg)

        if len(cpu) == 0:
            avg_cpu = sum(cpu)
        else:
            avg_cpu = sum(cpu) / len(cpu)

        return avg_cpu

    # Get HTTP request rate of the worker in past 30 min
    def inst_HTTP(self, inst_id):
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(inst_id)
        time_point = datetime.utcnow()
        time_period = 30  # data for 30 minutes

        http_rate = []  # A list to store HTTP request rate in past 30 min
        HTTP = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='RequestCountPerTarget',
            Dimensions=[
                {
                    'Name': 'TargetGroup',
                    'Value': config.target_group_dimension
                },
            ],
            StartTime=datetime.utcnow() - timedelta(seconds=time_period * 60),
            EndTime=time_point,
            Period=60,
            Statistics=['Sum']
        )
        for data_point in HTTP['Datapoints']:
            http_rate.append(int(data_point['Sum']))
        x_axis = list(range(0, len(http_rate)))

        return x_axis, http_rate

    # Count the number of workers in past 30 minutes
    def number_workers(self):
        # print('awsManager: getting the worker number history.')
        time_point = datetime.utcnow()
        time_period = 30 # data for 30 minutes
        inst_num = []  # A list to store number of workers in past 30 min

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
            Statistics=['Average']
            )
        # Save the count number into inst_num as an integer
        for data_point in inst_number['Datapoints']:
            inst_num.append(int(data_point['Average']))

        x_axis = list(range(0, len(inst_num)))

        print("Instance number ", inst_number)
        # print('X test', x_axis)
        # print('Y test', inst_num)
        # print('awsManager: worker number history complete.')

        return x_axis, inst_num

    # Create a ec2 instance
    def create_new_instance(self):
        try:

            response = self.ec2.create_instances(
                # ImageId=config.image_id,
                # MinCount=1,
                # MaxCount=1,
                # InstanceType='t2.medium',
                # KeyName=config.key_pair,
                # Monitoring={'Enabled': True},
                # TagSpecifications=config.tag_specifications_allen,
                # Placement=config.placement_allen,
                # SecurityGroups=[config.security_group_allen],
                # IamInstanceProfile=config.iam_arn_allen,
                # UserData=config.user_data
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

            print('Adding new instance ', new_instance, '...')
            # Wait for state to change before register it to a target group
            new_instance.wait_until_running(
                Filters=[
                    {
                        'Name': 'instance-id',
                        'Values': [new_instance.id]
                    }
                ]
            )
            print("wait until running...")
            new_instance.reload()

            # Register to a target group
            response = self.register_to_target_group(new_instance)
            print("registered to a target group :", response)

            instances = self.get_user_instances("running")
            instance_id = []
            for instance in instances:
                instance_id.append(instance.id)
            print('Our worker pool has', len(instance_id), "instances running currently.")

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
            # TargetGroupArn=config.target_group_arn_allen,
            # Targets=[{
            #     'Id': instance.id
            # }])
            TargetGroupArn=config.target_arn,
            Targets=[{
                'Id': instance.id
            }])

        # check response
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Successfully registered targets! Code - 200")

            return response['ResponseMetadata']['HTTPStatusCode']
        else:
            print("Register targets failed!")
            return -1

    def remove_instance(self, instanceId):
        response = self.elb.deregister_targets(
            # TargetGroupArn=config.target_group_arn_allen,
            # Targets=[
            #     {
            #         'Id': instanceId,
            #     },
            # ]
            TargetGroupArn=config.target_arn,
            Targets=[
                {
                    'Id': instanceId,
                },
            ]
        )

        print("Removing an instance")
        print(response)

        # Unregister an instance from the target group

        self.unregister_from_target_group(instanceId)

        # Terminate instance by instanceId
        self.ec2.instances.filter(InstanceIds=[instanceId]).terminate()
        print("Instance i " + instanceId + " is terminated")

        time.sleep(20)  # Delay for 20 seconds.

        instances = self.get_user_instances("running")
        instance_id = []
        for instance in instances:
            instance_id.append(instance.id)
        print('Our worker pool has', len(instance_id), "instances running currently")
        # TODO:  catch exception

    # Unregister an instance from the target group
    def unregister_from_target_group(self, instanceId):

        # Wait for deregister
        waiter = self.elb.get_waiter('target_deregistered')
        waiter.wait(
            # TargetGroupArn=config.target_group_arn_allen,
            # Targets=[
            #     {
            #         'Id': instanceId
            #     },
            # ],
            # WaiterConfig={
            #     'Delay': 15,
            #     'MaxAttempts': 40
            # }
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
            print("There are more than one pending/stopping instance")
            return False
        elif len(healthy_ids) != len(running_ids):
            print("# Healthy instances not equal to # running instances")
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

        print("remove ids are ", remove_id)

        for id in remove_id:
            self.remove_instance(id)


    def terminate_all(self):
        # Stop all workers
        instances = self.get_user_instances('running')
        inst_id = []
        for instance in instances:
            inst_id.append(instance.id)
        print("Currently there are ", len(inst_id), " running instances")

        for id in inst_id:
            print("We are removing instance", id, "...")
            self.remove_instance(id)
            print('This worker instance: {} has been removed successfully.'.format(id))

        # Stop manager
        manager_instance = self.ec2.instances.filter(InstanceIds=[config.manager_instance])
        manager_instance.stop()
        print("Manager is stopped")


    def clear_s3(self):
        bucket = self.s3.Bucket(config.s3_name)
        bucket.objects.all().delete()
        print("S3 data are deleted")



