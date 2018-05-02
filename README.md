# ReadWriteDelete
PoC for authentication/authorization using Django for a webapp and Flask for an API

This project is a proof of concept of using Auth0 to authorize and authenticate a web application that communicates with an API.
The basic idea is simple: the web app manages data (key/value pairs). Users must authenticate - only authenticated users can have access to the data.
Users can have one of three permissions: read, write, and delete.

CURRENT STATUS: the project contains a simple webapp and API.
The webapp authenticates via Auth0's Authorization Code Flow.
No authorization is done yet, either in the webapp or the API.
Both the webapp and the API use Python 3, and assume that django, flask, requests, social-auth-app-django, and python-dotenv are installed.
The webapp is written in Django and can be run via
( cd webapp/Auth0PoC/ ; python3 manage.py runserver )
I am using a slightly strange approach to the database: I use Django's ORM (for makemigrations and migrate) to manage the database schema, but the django app
does not actually connect to the database. The API does that instead.

The API is written in Flask and can be run via
( cd webapp/Auth0PoC/scripts ; ./api.py )

NEXT STEP: do Auth0 authorization for integrating the webapp with the API.

CAVEATS:
1) Neither the API nor the webapp use https. They really should.
2) This is only set up for local testing. If interested, I could set up a production server on auth0.johngateley.com.
3) This really should have automated testing (unit tests, integration tests, end-to-end tests etc.) but I haven't put them in.

