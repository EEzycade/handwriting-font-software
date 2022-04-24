write "     ***  If this doesn't work, make sure you have updated pip: pip install --upgrade pip"
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
.\env\Scripts\activate; $env:FLASK_APP = "app"; $env:FLASK_ENV = "development"
write ""
write ""
write "     ***  TO RUN, TYPE: flask run  ***"