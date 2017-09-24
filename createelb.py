#####
#
# Creates RDS instance for Wordpress
# createelb.py 
#
#####

import boto3
import sys, json, time
import conf

elb=boto3.client('elbv2')
ec2=boto3.client('ec2')
ec2r=boto3.resource('ec2')

#create target group
try: 
	#Possibly dangerous assumptions: should only be one VPC, get it.
	vpcid = ec2.describe_vpcs()['Vpcs'][0]['VpcId']

	response = elb.create_target_group(
		Name='jbme-tg',
		Protocol='HTTP',
		Port=80,
		VpcId=vpcid,
		HealthCheckProtocol='HTTP',
		HealthCheckPort='80',
		HealthCheckPath='/',
		HealthCheckIntervalSeconds=30,
		HealthCheckTimeoutSeconds=5,
		HealthyThresholdCount=5,
		UnhealthyThresholdCount=2,
		Matcher={
			'HttpCode': '200,302'
		},
		TargetType='instance'
	)
except Exception as e:
	print "Failed to create Target Group:"
	print e
	sys.exit()
print "Created Target Group"

# Create Security group for ELB
try:
	response = ec2.create_security_group(
	Description='jbme-elb-sg',
	GroupName='jbme-elb-sg',
	VpcId=vpcid
	)
	sgid = response['GroupId']
	print "Created Security Group"
except Exception as e:
	print "Failed to create Security Group"
	print e
	sys.exit()

# Add rules to sg
try:
	response = ec2.authorize_security_group_ingress(
	    GroupId=sgid,
	    IpPermissions=[
	        {
	            'FromPort': 80,
	            'IpProtocol': 'tcp',
	            'IpRanges': [
	                {
	                    'CidrIp': '0.0.0.0/0',
	                    'Description': 'All'
	                },
	            ],
	            'Ipv6Ranges': [
	                {
	                    'CidrIpv6': '::/0',
	                    'Description': 'All'
	                },
	            ],
	            'ToPort': 80,
	        }
	        
	    ]
	)
	response = ec2.authorize_security_group_ingress(
	    GroupId=sgid,
	    IpPermissions=[
	        {
	            'FromPort': 443,
	            'IpProtocol': 'tcp',
	            'IpRanges': [
	                {
	                    'CidrIp': '0.0.0.0/0',
	                    'Description': 'All'
	                },
	            ],
	            'Ipv6Ranges': [
	                {
	                    'CidrIpv6': '::/0',
	                    'Description': 'All'
	                },
	            ],
	            'ToPort': 443,
	        }
	        
	    ]
	)
except Exception as e:
	print "Failed to create Security Group rules"
	print e
	sys.exit()

print "Added egress rules to Security Group"


try:
	#need subnets
	subnets = ec2.describe_subnets()['Subnets']
	vpcsubnets=[]
	for subnet in subnets:
		vpcsubnets.append(subnet['SubnetId'])

	response = elb.create_load_balancer(
	Name='jbme-elb',
	Subnets=vpcsubnets,
	SecurityGroups=[
		sgid,
	],
	Scheme='internet-facing',

	Type='application',
	IpAddressType='ipv4'
)
except Exception as e:
	print "Failed to create ELB"
	print e
print "Successfully created ELB"
#create elb