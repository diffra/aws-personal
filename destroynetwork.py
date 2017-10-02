import boto3, sys, time, yaml
import conf
import jaws

ec2=boto3.client('ec2')

with open("network.yml", 'r') as stream:
    try:
        network=yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


if network['igw']==True:
    try:
        print("Detaching IGW.")
        #get IGW ID
        igwid=ec2.describe_internet_gateways(
            Filters=[{'Name': 'attachment.vpc-id', 'Values': [conf.vpcid]}]
        )['InternetGateways'][0]['InternetGatewayId']
        #detatch from VPC
        response = ec2.detach_internet_gateway(
            InternetGatewayId=igwid,
            VpcId=conf.vpcid
        )
        #wait for detach before delete
        for i in range(1,100,1):
            time.sleep(5)
            response=ec2.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [conf.vpcid]}]
            )
            igws=len(response['InternetGateways'])
            print("Found %i attached IGWs" % igws)
            if len(response['InternetGateways']) == 0:
                print("Successfully detached IGW from VPC")
                break
            if i==100:
                print("IGW never detached from VPC. Moving on anyway.")
        response = ec2.delete_internet_gateway(
            InternetGatewayId=igwid
        )
        #now delete IGW and confirm.
        for i in range(1,100,1):
            time.sleep(5)
            response=ec2.describe_internet_gateways(
                Filters=[{'Name': 'internet-gateway-id', 'Values': [igwid]}]
            )
            if len(response['InternetGateways']) == 0:
                print("Successfully deleted IGW")
                break
            if i==100:
                print("IGW never detached from VPC. Moving on anyway.")

    except Exception as e:
        print("Failed deleting igw.")
        print(e)

#Delete subnets
# First get list of subnets in this VPC
response = ec2.describe_subnets(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                conf.vpcid,
            ]
        },
    ]
)

for subnet in response['Subnets']:
    print("Deleting Subnet: %s" % subnet['SubnetId'])
    jaws.delete_subnet(subnet['SubnetId'])
