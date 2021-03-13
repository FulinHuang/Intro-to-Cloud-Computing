import os

# balancer
arn = 'arn:aws:elasticloadbalancing:us-east-1:411033800461:loadbalancer/app/loadbalancer/36142359a6458967'
dns = 'loadbalancer-1947271922.us-east-1.elb.amazonaws.com'
target_arn = 'arn:aws:elasticloadbalancing:us-east-1:411033800461:targetgroup/1779lb/76c209c218e6fc76'
target_group_dimension = 'targetgroup/allena2/c1b769c7b4575737'
ELB_dimension = 'app/loadbalancer/3a7654beb0b62d6f'


# Variable for creating an instance
ImageId ='ami-03b4f4239f819d507'
KeyName ='ece1779-manager'
user_tag = 'user'
user_placement = 'usergroup'
manager_tag = 'manager'
tag_specificatios = [{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': user_tag}]}]
placement = {'AvailabilityZone': 'us-east-1a', 'GroupName': user_placement}
security_group = 'launch-wizard-7'
iam_instance_profile = {'Arn': 'arn:aws:iam::411033800461:instance-profile/full_s3_access_from_ec2'}
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
./start.sh
--//
'''

class Config(object):
    SECRET_KEY = 'ECE1779'
    SQLALCHEMY_DATABASE_URI = 'mysql://allen_admin:lu19920218@allen-ece1779-a1.c7mezzt0p0rf.us-east-1.rds.amazonaws.com/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


