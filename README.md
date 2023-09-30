# Task 1
1. Create the virtual environment for Python and install dependencies:
```shell
$ cd task1
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

2. Run FastAPI:
```shell
$ uvicorn main:app --reload
```

3. Use the web interfact at http://127.0.0.1:8000/docs. Or alternatively, run the following curl:
```shell
$ curl -X 'GET' 'http://127.0.0.1:8000/bin/920140000084' -H 'accept: application/json'
```

# Task 2
1. Create the virtual environment for Python and install dependencies:
```shell
$ cd task2
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

2. Run PostgreSQL and pgAdmin 4 using Docker Compose:
```shell
$ docker compose up
```

3. Run the Python script to populate the empty database with data:
```shell
$ python main.py
```

4. Access pgAdmin at http://localhost:8888/browser/ to run your SQL queries and analyze the data. Refer to `compose.yaml` file to find the credentials to access both the pgAdmin and connect to the Postgre database.