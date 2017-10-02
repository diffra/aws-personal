import boto3

ec2=boto3.client('ec2')
def create_subnet(vpcid, cidr, az):
    #Create Subnet VPC
    response = ec2.create_subnet(
        VpcId=vpcid,
        CidrBlock=cidr,
        AvailabilityZone=az
    )
    return response['Subnet']['SubnetId']
def delete_subnet(id):
    response = ec2.delete_subnet(
        SubnetId=id
    )
    return response
def tag_ec2(id,tag,value):
    response = ec2.create_tags(
        Resources=[
            id,
        ],
        Tags=[
            {
                'Key': tag,
                'Value': str(value)
            },
        ]
    )
