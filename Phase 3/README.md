# 6400Summer18Team06
Repository for 6400Summer18Team06

# App Setup
This application uses Python3, Flask, and MySQL.

After installing Python3, install Flask and PyMySQL.

```pip3 install Flask```
```pip3 install PyMySQL```

MySQL needs to be installed separately. Update the username and password in **buildschema.py** and **sqlfunctions.py** to match a local MySQL admin's credentials. They are set as username:*admin* and password:*password* by default.

Run **buildschema.py** to initialize the database. 

Run **app.py** to start the app. The app will run on http://127.0.0.1:5000.
