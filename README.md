# Task 1
1. Create the virtual environment for Python and install dependencies:
```shell
$ cd task1_2
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