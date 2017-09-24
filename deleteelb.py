#####
#
# Creates RDS instance for Wordpress
# deleteelb.py 
#
#####


import boto3
import sys, json, time
import conf

elb=boto3.client('elbv2')
ec2=boto3.client('ec2')
ec2r=boto3.resource('ec2')


try:
	#get arn for target group
	tgarn=elb.describe_target_groups(Names=['jbme-tg'])['TargetGroups'][0]['TargetGroupArn']

	response = elb.delete_target_group(
    	TargetGroupArn=tgarn
	)
except Exception as e:
	print "Failed to delete target group"
	print e
	sys.exit()
print "Deleted Target Group %s" % (tgarn)

try:
	response = ec2.delete_security_group(
	    GroupName='jbme-elb-sg'
	)
except Exception as e:
	print "Failed to delete security group"
	print e
	sys.exit()
print "Deleted security Group"


try:
	#Get load balancer ARN
	lbarn = elb.describe_load_balancers(
        Names=[
        'jbme-elb'
    	],
	)['LoadBalancers'][0]['LoadBalancerArn']
	response=elb.delete_load_balancer(LoadBalancerArn=lbarn)
except:
	print "Failed to delete ELB"
	print e
	sys.exit()
print "Deleted ELB"
