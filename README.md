# flickr

### Instructions to Setup Project

##### Setup Virtual Environment

* python3 -m venv venv

##### Activate Virtual Environment 

* source venv/bin/activate

##### Install python packages from requirements.txt

* pip install -r requirements.txt

##### Create migrations

* python manage.py makemigrations

##### Migrate to Database

* python manage.py migrate

##### Create Superuser (same used for Photos & Django Admin)

* python manage.py createsuperuser

##### Setup Database

* python setupdb.py

##### Run Project on locally on port 8000

* python manage.py runserver

## API Documentation

* Swagger - `localhost:8000`

* DRF Browsable API - `localhost:8000/api/v1`

* [Postman Collection](https://www.getpostman.com/collections/47cb16efe6ad42a36611)


