import boto3, sys, yaml
import conf
import jaws
ec2 = boto3.client('ec2')

#ec2.create_internet_gateway()['InternetGateway']['InternetGatewayId']
with open("network.yml", 'r') as stream:
    try:
        network=yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)

if network['igw']==True:
    try:
        igwid=ec2.create_internet_gateway()['InternetGateway']['InternetGatewayId']
        ec2.attach_internet_gateway(
            InternetGatewayId=igwid,
            VpcId=conf.vpcid
        )
    except Exception as e:
        print("Failed to create IGW: %s" % e)

print("Creating Subnets...")
for subnet in network['subnets']:
    try:
        print(subnet)
        net=network['subnets'][subnet]
        subnetid=jaws.create_subnet(conf.vpcid,net['cidr'],net['az'])
        jaws.tag_ec2(subnetid, 'Name', subnet)
    except Exception as e:
        print("Failed to create subnet: %s" % e)


#print(create_subnet (conf.vpcid, '10.10.1.0/24', 'us-west-2a'))
