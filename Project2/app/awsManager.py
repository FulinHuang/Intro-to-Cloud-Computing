import boto3
from app import config
from botocore.exceptions import ClientError

class Manager:

    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')

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



