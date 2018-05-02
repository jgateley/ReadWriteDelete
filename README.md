# ReadWriteDelete
PoC for authentication/authorization using Django for a webapp and Flask for an API

This project is a proof of concept of using Auth0 to authorize and authenticate a web application that communicates with an API.
The basic idea is simple: the web app manages data (key/value pairs). Users must authenticate - only authenticated users can have access to the data.
Users can have one of three permissions: read, write, and delete.

CURRENT STATUS: the project contains a simple webapp and API with no authentication or authorization yet.
Both use Python 3, and assume that django, flask and requests are installed.

The webapp is written in Django and can be run via
( cd webapp/Auth0PoC/ ; python3 manage.py runserver )
I am using a slightly strange approach to the database: I use Django's ORM (for makemigrations and migrate) to manage the database schema, but the django app
does not actually connect to the database. The API does that instead.

The API is written in Flask and can be run via
( cd webapp/Auth0PoC/scripts ; ./api.py )

NEXT STEP: start with Auth0 authentication.

CAVEATS:
1) Neither the API nor the webapp use https. They really should.
2) This is only set up for local testing. If interested, I could set up a production server on auth0.johngateley.com.
