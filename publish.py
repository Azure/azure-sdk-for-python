####
# This script demonstrates how to use the Tableau Server Client
# to publish a workbook to a Tableau server. 
# The script will call config.py another python program which holds
# the credentials of DEV/UAT/PROD. User is promted to input to which
# environment the workbooks need to be published. According to the user's
# input the respective credentials are set to the variables.
# It will publish all the workbooks from the source directory
# to the destination project of the given server.
# 
# Note: The REST API publish process cannot automatically include
# extracts or other resources that the workbook uses. Therefore,
# a .twb file with data from a local computer cannot be published,
# unless packaged into a .twbx file.
#
# For more information, refer to the documentations on 'Publish Workbook'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####
import glob
import tableauserverclient as TSC
from tableauserverclient import ConnectionCredentials, ConnectionItem

exec(open('config1.py').read())
environ = input('Enter the environment (DEV/UAT/PROD)= ')
if (environ == 'DEV'):
	username = username_dev
	password = password_dev
	sitename = sitename_dev
	url = url_dev
	sourcedir = sourcedir_dev
	destdir = destdir_dev
elif (environ == 'UAT'):
	username = username_uat
	password = password_uat
	sitename = sitename_uat
	url = url_uat
	sourcedir = sourcedir_uat
	destdir = destdir_uat
elif (environ == 'PROD'): 
	username = username_prod
	password = password_prod
	sitename = sitename_prod
	url = url_prod
	sourcedir = sourcedir_prod
	destdir = destdir_prod
else :
	print (' Wrong input exiting program')
	exit()
print('publishing to '+environ+' environment')
path = sourcedir
def main():
  # Step 1: Sign in to server.
  #  tableau_auth = TSC.TableauAuth(username, password)
  #  server = TSC.Server(server)
	tableau_auth = TSC.TableauAuth(username, password, sitename)
	server = TSC.Server(url)
	overwrite_true = TSC.Server.PublishMode.Overwrite

	with server.auth.sign_in(tableau_auth):

        # Step 2: Get all the projects on server, then look for the destination project.
		all_projects, pagination_item = server.projects.get()
		default_project = next((project for project in all_projects if project.name == destdir), None)

        # Step 3: If destination project is found, form a new workbook item and publish.
		if default_project is not None:
			new_workbook = TSC.WorkbookItem(default_project.id)
			files = [f for f in glob.glob(path + "**/*.twbx", recursive=True)]
			for f in files:
				sourcedir = f
				new_workbook = server.workbooks.publish(new_workbook, sourcedir, overwrite_true)
				print("Workbook published. ID: {0}".format(new_workbook.id))
		else:
			error = "The destination project could not be found."
			raise LookupError(error)

if __name__ == '__main__':
    main()
