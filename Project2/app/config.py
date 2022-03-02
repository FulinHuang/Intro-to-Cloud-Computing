

# YW
# balancer
arn = 'arn:aws:elasticloadbalancing:xxx'
dns = 'xxx.us-east-1.elb.amazonaws.com'
target_arn = 'arn:aws:elasticloadbalancing:xxx'
target_group_dimension = 'targetgroup/xxx'
ELB_dimension = 'app/xxxELB/xxx'

# S3
s3_name = 'ece1779yw'

# Variable for creating an instance

ImageId = 'ami-xxx' # worker creation
KeyName = 'Allen_A2_User1'
user_tag = 'user'
user_placement = 'a2user'  # worker list filter, user creation
manager_tag = 'manager'
manager_instance = 'i-09ee913b4cxxxxx'
tag_specifications = [{
    'ResourceType': 'instance',
    'Tags': [{'Key': 'Name', 'Value': user_tag}]}]
placement = {'AvailabilityZone': 'us-east-1f', 'GroupName': user_placement}
security_group = 'launch-wizard-3'
iam_instance_profile = {'Arn': 'arn:aws:iam::xxxx:instance-profile/S3_RDS_FULL'}
user_data = '''Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="cloud-config.txt"

#cloud-config
cloud_final_modules:
- [scripts-user, always]

--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
cd /home/ubuntu/Desktop
./start.sh
--//
'''


class Config(object):
    SECRET_KEY = 'ECE1779'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:xxx'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
