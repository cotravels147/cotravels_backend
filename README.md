<!-- To setup project follow the following Steps-->

<!-- create a virtual environment venv using the following commands -->
pip install virtualenv
python3 -m venv <myenvname>

<!-- to activate the virtual environment run the following command -->
.\<myenvname>\Scripts\activate

<!-- After virtual environment is active install all the dependencies from requirements.txt -->
pip install -r requirements.txt 

<!-- command to start application -->
uvicorn app.main:app --reload

<!-- command to execute migration -->
alembic -c alembic.ini revision --autogenerate -m "YOUR MESSAGE"
alembic -c alembic.ini upgrade head

<!-- command to update requirements.txt with required versions of packages -->
pip freeze > requirements.txt