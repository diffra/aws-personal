#####
#
# Creates RDS instance for Wordpress
# createrds.py dbname
#
#####

import boto3
import sys, json, time, MySQLdb
import conf

dbname=sys.argv[1]

rds = boto3.client('rds')
r53 = boto3.client('route53')
s3  = boto3.resource('s3')
bucket=s3.Bucket('jb-web')
# fails with DBInstanceAlreadyExists if DB already exists.

try:
	response = rds.create_db_instance(
		DBInstanceIdentifier=dbname,
		MasterUsername=conf.dbuser,
		MasterUserPassword=conf.dbpass,
		DBInstanceClass='db.t2.micro',
		Engine='mariadb',
		AllocatedStorage=5)
	print "Submitted request. Database Creating..."
	time.sleep(10)
	#wait for create to finish
	for wait in range (0,300):
		status=rds.describe_db_instances(DBInstanceIdentifier=dbname)['DBInstances'][0]['DBInstanceStatus']
		if status=="available":
			print "Status: %s" % (status)
			hostname=rds.describe_db_instances(DBInstanceIdentifier=dbname)['DBInstances'][0]['Endpoint']['Address']
			print "DNS entry for Database: %s" % (hostname)
			break
		print "Status: %s" % (status)
		time.sleep(5)
		if wait==300:
			print "Database creation timed out"
			sys.exit()
except Exception as error:
	print "Failed to create database:"
	print error

#import DB from s3
try: 
	#get sql file
	bucket.download_file("wordpress.sql","/tmp/wordpress.sql")
	# Connect to SQL
	db = MySQLdb.connect(host=hostname,  # your host 
					 user=conf.dbuser,	   # username
					 passwd=conf.dbpass
					 )   # name of the database
	cur = db.cursor()
	# read in queries
	f = open('/tmp/wordpress.sql', 'r')
	query = " ".join(f.readlines())
	# Execute
	cur.execute(query)
	print "Database import succeeded"
except Exception as error:
	print "Failed to import database"
	print error