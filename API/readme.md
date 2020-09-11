As of now there is currently a running instance of our API on Google Cloud servers at the following address:
https://code3visionary.appspot.com/

This API has a NoSQL database implemented to contain the id, number of calls, year, location, and cause of the call into a database.
To interact with these features I have implemented a few requests that can be use to insert new data, retrieve data, and delete entry from the database.

#### List of Requests:
### GET:
https://code3visionary.appspot.com/calls -- This will return all the calls in the database no matter the year, cause, or location
https://code3visionary.appspot.com/calls/{ID} -- With a specific ID a user can retrieve a specific call they are looking for 
https://code3visionary.appspot.com/calls/query/?year=2015&location=2701&cause=321 -- If the user does not know the ID but still wants to obtain the call count, they can use this GET request and supply the year, location, and cause to just retrieve the call count with that specific information.

### POST:
https://code3visionary.appspot.com/calls

raw body:

  {
  
    "cause":"test",
    
    "year": 2000,
    
    "location": 10001,
    
    "callcount": 150
    
  }
  
This POST request will insert an entry into the database with the number of calls being 150, the location being 10001 (TAZ), the year being 2000, and the cause being "test". The ID is self generated and will be output to the user once the POST was successful.

### DELETE:
https://code3visionary.appspot.com/calls/{ID} -- Deletes the entry from the database with the specific ID of that entry.

#### Prerequisite
-Google account

-Python 2.7

Note: If you have Anaconda for python 2.7 install this would work too

#### Installation
To get started on hosting your own API to GCloud, I recommend looking at this page:
https://cloud.google.com/appengine/docs/standard/python/quickstart

1. Click on the "Go to App Engine" button and create a new server for your account and go through the process of creating your own server name.
Note: You will need a google account to set this up.

2. Go back to the quickstart page and click on "Download the SDK"

3. Under "Install and initialize Google Cloud SDK:" click the download button. 
This will take you to a page where you can download the SDK for your provided OS.
Choose the one that best fits you and follow its instructions.
I will be assuming you are using Windows in this tutorial.

4. Click on the blue link "Cloud SDK installer"
Save the installer somewhere and run through the installation with defaults.

5. Once the installer finishes press next and keep all the boxes checked for simplicity.
A new command line window will open and it will ask you to sign into your Google account.

6. Once you have logged in it will then ask you to choose a cloud project to link to.
Choose the one you've setup at the beginning of this tutorial.

7. Keep the command line window open and run the following commmand:
gcloud components install app-engine-python
Press Y and Enter on the new command prompt that will install the python component of GCloud.

8. Once the python component finishes installing, close that command prompt and go back to the original Gcloud command prompt and run this command:
gcloud components install app-engine-python-extras
Press Y and Enter to start the installation for extra python components.

9. Once the extra components finishes, close that window.
Go back to your Gcloud window and run the following commands:
gcloud components update
This updates all the components to make sure we're running with the most recent version.
Press Y and Enter to start the installation.

10. Once the components finish updating, close that command prompt and as well as the Gcloud command prompt.

11. Open up the Google Cloud SDK Shell which should be in your start menu but if not can be found here:
C:\Users\Kien Tran\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Google Cloud SDK
Navigate to where the API folder lives in this repository and make sure that app.yaml is in the current working directory.

12a. To run the API locally use the following commands:
dev_appserver.py app.yaml
This will setup the API to run on port 8080 on your local machine.
To get to it, open a internet browser and navigate to http://localhost:8080
You will know it is running when you see the words "The Visionary's Call Predictor"
This also opens the port 8000 so you can have backend access to your API.
Allowing you to see what is in the database and see some statistics
To close the local deployment, press Ctrl+C in the Google Cloud SDK Shell


12b. To deploy your API on Google's Cloud Platform run the following commands:
gcloud app deploy
This will deploy your instance on Google's server and can be access using the following commands:
gcloud app browse
This command will open your default browser and navigate to where your instance lives.
From here you can now make requests using URLs above, and you can check statistics on your instance through Google's UI control panel:
https://console.cloud.google.com/home?project=code3visionary

This is where this tutorial ends.
You can find more information on Google's Cloud Platform as well as tutorials on add additional APIs to your instance, create private keys for only certain users or even setup OAuth 2.0 Authentication.
