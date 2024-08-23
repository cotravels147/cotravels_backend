<!-- command to start application -->
uvicorn app.main:app --reload

<!-- command to execute migration -->
alembic -c alembic.ini revision --autogenerate -m "YOUR MESSAGE"
alembic -c alembic.ini upgrade head