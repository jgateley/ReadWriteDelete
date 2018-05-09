# ReadWriteDelete
PoC for authentication/authorization

This project is a proof of concept of using Auth0 to authorize and authenticate a web application that communicates with an API.
The basic idea is simple: the web app manages data (key/value pairs). Users must authenticate - only authenticated users can have access to the data.
Users can have a subset of three permissions: read, write, and delete.

CURRENT STATUS: the project contains a simple webapp, a tester script, an API and a scope rule.
The webapp authenticates via Auth0's Authorization Code Flow.
The tester script authenticates via Auth0's Client Credentials grant.
The API requires an authenticated caller.
Users have a subset of the three permissions (scopes) read:data, write:data and delete:data.
The scope rule grants all three permissions (like an admin) to john.gateley@gmail.com, otherwise it only grants read and write.

There is a django webapp, but this is work-in-progress, and not functional.
The django app is used for database management (database migrations).
The API connects via the django ORM code to the database.
The database is Postgresql, and is named auth0. It must be created before running the webapp
To ensure the database exists:
psql
create database auth0 ;
\q
( cd webapp/Auth0PoC/ ; python3 manage.py makemigrations ; python3 manage.py migrate )

Both the webapp and the API use Python 3, and assume that django, flask, requests, social-auth-app-django, and python-dotenv are installed.
There is a requirements.txt file for all the python packages required

The API is written in Flask and can be run via
( cd webapp/Auth0PoC/scripts ; ./api.py )
The API requires callers to be authenticated and authorized.

There is a test script webapp/Auth0PoC/scripts/test_token.py which will exercise the API and test 3 cases:
1) Not authenticated
2) Properly authenticated and authorized
3) Improperly authenticated
Future work: Test individual scopes

The WebApp is written in flask and can be run via:
( cd webapp/Auth0PoC/webapp ; python3 webserver.py )

CAVEATS:
1) Neither the API nor the webapp use https. They really should, as there is no security without this.
2) This is only set up for local testing. If interested, I could set up a production server on auth0.johngateley.com.
3) It really needs more automated testing, the single test script is just a start


