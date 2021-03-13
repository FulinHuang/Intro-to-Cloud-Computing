import boto3
from app import config
from datetime import datetime, timedelta


# Get CPU utilization of the worker in past 30 min from cloudwatch
def inst_CPU(inst_id):
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(inst_id) # Identify the instance by ID
    watch = boto3.client('cloudwatch')
    start = 31
    end = 30  # the fist time interval is 31 to 30
    CPU_utl = []     # A list to store CPU utilization in past 30 min
    for times in range(0, 30):
        CPU = watch.get_metric_statistics(
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


    x_axis =list(range(1, 31))
    return x_axis, CPU_utl

# Get HTTP request rate of the worker in past 30 min
def inst_HTTP(inst_id):
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
def number_workers():
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


# Choose the running instances
def select_running_inst():
    ec2 = boto3.resource('ec2')
    # Find all running instances
    instances = ec2.instances.filter(
        Filters=[

            {'Name': 'placement-group-name',
             'Values': [config.worker_group]},

            {'Name': 'instance-state-name',
             'Values': ['running']},

            {'Name': 'image-id',
             'Values': [config.image_id]},

        ]
    )

    inst_id = []
    for instance in instances:
        inst_id.append(instance.id)  # List of the running instance IDs
    print('We have {} instances now!'.format(len(inst_id)))
    print(inst_id)
    return instances  # Return the running instances