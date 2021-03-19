import os
#YW
# balancer
arn = 'arn:aws:elasticloadbalancing:us-east-1:489711376857:loadbalancer/app/a2LoadBalancer/2fdf1cd188e91767'
dns = 'a2LoadBalancer-472858139.us-east-1.elb.amazonaws.com'
target_arn = 'arn:aws:elasticloadbalancing:us-east-1:489711376857:targetgroup/workerpool5000/2a590f2f6b003750'
target_group_dimension = 'targetgroup/workerpool5000/2a590f2f6b003750'
ELB_dimension = 'app/a2LoadBalancer/2fdf1cd188e91767' # worker list filter

# S3
s3_name = 'ece1779yw'

# Variable for creating an instance
ImageId = 'ami-0cf5fc8b139494295' # worker creation
KeyName = 'ece1779a1aij'
user_tag = 'user'
user_placement = 'a2user' # worker list filter, user creation

manager_tag = 'manager'
manager_instance = 'ami-0cf5fc8b139494295'

tag_specificatios = [{
	'ResourceType': 'instance',
	'Tags': [{'Key': 'Name', 'Value': user_tag}]}]
placement = {'AvailabilityZone': 'us-east-1f', 'GroupName': user_placement}
security_group_Irene = 'launch-wizard-3'
iam_instance_profile = {'Arn': 'arn:aws:iam::489711376857:instance-profile/S3_RDS_FULL'}
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
    # SQLALCHEMY_DATABASE_URI = 'mysql://allen_admin:lu19920218@allen-ece1779-a1.c7mezzt0p0rf.us-east-1.rds.amazonaws.com/dbname'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:ece1779a2@database-1.c6ylehamglk7.us-east-1.rds.amazonaws.com/database1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
