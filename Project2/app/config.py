import os

############ALLEN#############
image_id = 'ami-0a1a1906efbd4c711'
key_pair = 'Allen_A2_User1'
security_group_allen = 'launch-wizard-1'
worker_group = 'User_group_2'  # placement group for workers
worker_group_2 = 'usergroup'  # placement group for workers
manager_group = 'managergroup'  # placement group for managers

placement_allen = {'AvailabilityZone': 'us-east-1d', 'GroupName': worker_group}
elb_arn = 'arn:aws:elasticloadbalancing:us-east-1:011441637402:loadbalancer/app/allena2ELB/5360f782e6428bc4'
elb_dns = 'allena2ELB-168220349.us-east-1.elb.amazonaws.com'
elb_name = 'allena2ELB'
target_group_arn_allen = 'arn:aws:elasticloadbalancing:us-east-1:011441637402:targetgroup/allena2/c1b769c7b4575737'
iam_arn_allen = {'Arn': 'arn:aws:iam::011441637402:instance-profile/full_S3_access_from_EC2'}
target_group_dimension_allen = 'targetgroup/allena2/c1b769c7b4575737'
ELB_dimension_allen = 'app/allena2ELB/5360f782e6428bc4'
tag_specifications_allen = [{
    'ResourceType': 'instance',
    'Tags': [{'Key': 'Name', 'Value': 'Allen - add worker_0316'}]}]
################################

# # balancer
# arn = 'arn:aws:elasticloadbalancing:us-east-1:411033800461:loadbalancer/app/load-balancer-1/254882bfbf58fc6e'#'arn:aws:elasticloadbalancing:us-east-1:411033800461:loadbalancer/app/loadbalancer/36142359a6458967'
# dns =  'load-balancer-1-1434705320.us-east-1.elb.amazonaws.com' #'loadbalancer-1947271922.us-east-1.elb.amazonaws.com'
# target_arn = 'arn:aws:elasticloadbalancing:us-east-1:411033800461:targetgroup/1779lb1/35b8955c88fb5be1'#'arn:aws:elasticloadbalancing:us-east-1:411033800461:targetgroup/1779lb/76c209c218e6fc76'
# target_group_dimension = 'targetgroup/1779lb1/35b8955c88fb5be1'#'targetgroup/1779lb/76c209c218e6fc76'
# ELB_dimension = 'app/load-balancer-1/254882bfbf58fc6e' #'app/loadbalancer/36142359a6458967'
#
# # S3
# s3_name = 'bucket1779'
#
# # Variable for creating an instance
# ImageId = 'ami-0cf5fc8b139494295'   #'ami-03b4f4239f819d507'
# KeyName = 'ece1779-manager'
# user_tag = 'user'
# user_placement = 'usergroup'
# manager_tag = 'manager'
# manager_instance = 'i-0530347cfe20bd7ff'
# tag_specificatios = [{
#     'ResourceType': 'instance',
#     'Tags': [{'Key': 'Name', 'Value': user_tag}]}]
# placement = {'AvailabilityZone': 'us-east-1f', 'GroupName': user_placement}
# security_group_Irene = 'launch-wizard-7'
# iam_instance_profile = {'Arn': 'arn:aws:iam::411033800461:instance-profile/full_s3_access_from_ec2'}
# user_data = '''Content-Type: multipart/mixed; boundary="//"
# MIME-Version: 1.0
#
# --//
# Content-Type: text/cloud-config; charset="us-ascii"
# MIME-Version: 1.0
# Content-Transfer-Encoding: 7bit
# Content-Disposition: attachment; filename="cloud-config.txt"
#
# #cloud-config
# cloud_final_modules:
# - [scripts-user, always]
#
# --//
# Content-Type: text/x-shellscript; charset="us-ascii"
# MIME-Version: 1.0
# Content-Transfer-Encoding: 7bit
# Content-Disposition: attachment; filename="userdata.txt"
#
# #!/bin/bash
# cd /home/ubuntu/Desktop
# ./start.sh
# --//
# '''

#YW
# balancer
arn = 'arn:aws:elasticloadbalancing:us-east-1:489711376857:loadbalancer/app/a2LoadBalancer/2fdf1cd188e91767'
dns = 'a2LoadBalancer-472858139.us-east-1.elb.amazonaws.com'
target_arn = 'arn:aws:elasticloadbalancing:us-east-1:489711376857:targetgroup/workerpool5000/2a590f2f6b003750'
target_group_dimension = 'targetgroup/workerpool5000/2a590f2f6b003750'
ELB_dimension = 'app/a2LoadBalancer/2fdf1cd188e91767'

# S3
s3_name = 'ece1779yw'

# Variable for creating an instance
ImageId = 'ami-0cf5fc8b139494295'
KeyName = 'ece1779a1aij'
user_tag = 'user'
user_placement = 'a2user'

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
    # SQLALCHEMY_DATABASE_URI = 'mysql://admin:ece1779a2@database-1.c6ylehamglk7.us-east-1.rds.amazonaws.com/database1'
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:ece1779pass@database-ece1779.cpng8nm7nagd.us-east-1.rds.amazonaws.com/userapp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
