# Developer Server

## Environment Setup

1. Make sure python is installed

2. Navigate to the app:

```
cd app
```

3. Create a virtual environment: 

```
python -m venv env
```

4. Activate the virtual environment:

On Windows:

```
.\env\Scripts\activate
```
On Linux:
```
source env/bin/activate
```

5. Make sure the latest version of pip is installed:

```
pip install --upgrade pip
```

6. Install the dependencies:

```
pip install -r requirements.txt
```

## Running the app

1. Navigate to the app:

```
cd app
```

2. Activate the venv (virtual environment):

```
.\env\Scripts\activate
```
On Linux:
```
source env/bin/activate
```

3. Set the app type:

```
$env:FLASK_APP = "app"
```

4. Set the flask environment (production, development, testing):

```
$env:FLASK_ENV = "development"
```

5. Run the server:

```
flask run
```


## Python Package Requirements

- Flask
