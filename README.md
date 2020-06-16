# Django-Movie-App

For this app to work, you need config files for google firestore and youtube api
After getting it registered, make a credentials.py file with the format:
apiKey = ""     # youtube API key
config = {        # API key for firebase
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": "",
    "serviceAccount": ""
} 

and save it as credentials.py under utils directory
Also download the serviceAccount file from firebase and save it in project root directory
