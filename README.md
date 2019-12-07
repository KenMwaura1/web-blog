[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

**Zoo Web Blog** 

This is a simple blogging web app created using Flask(server),Bootstrap(Frontend) and MongoDB as the database.
This application is still in active development and alot still needs to be done.


### **Quickstart**

git clone https://github.com/KenMwaura1/web-blog.git

cd into web-blog

create virtualenv `(python3 -m venv web-blog)` OR any name you prefer

activate virtualenv by `cd web-blog` OR {{venv name}} then `source bin/activate`

`python -m pip install -r requirements.txt`

Ensure have a mongodb server running locally on your system or via Docker on port 27017

Incase your configuration is different edit the `Database.py` to modify variables related to the database

Run the app by either setting the Flask env variables i.e `EXPORT FLASK_APP=app.py`

OR 

`python app.py`

Go to localhost:5000 to see the app running.

Basic api calls available via localhost:5000/posts and localhost:5000/blogs

