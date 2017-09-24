#####
#
# Deletes RDS instance for Wordpress
# deleterds.py dbname
#
#####

import boto3
import sys, json, time
import creds

dbname=sys.argv[1]

rds = boto3.client('rds')

# fails with DBInstanceAlreadyExists if DB already exists.

try:
	response = rds.delete_db_instance(
		DBInstanceIdentifier=dbname,
		SkipFinalSnapshot=True)
	print "Submitted request. Database Deleting..."
	time.sleep(10)

	#wait for delete to finish
	for wait in range (0,100):
		try:
			rds.describe_db_instances(DBInstanceIdentifier=dbname)
			print "Not yet deleted"
			time.sleep(5)
		#If the DB isn't there we're clear
		except rds.exceptions.DBInstanceNotFoundFault:
			print "Database successfully deleted"
			sys.exit()
		except Exception as error:
			print "Error deleting database:"
			print error
	print "Database still not deleted.  Giving up..."
except Exception as error:
	print "Error deleting database:"
	print error