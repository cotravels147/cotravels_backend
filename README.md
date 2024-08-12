<!-- command to start application -->
uvicorn app.main:app --reload

<!-- command to execute migration -->
alembic -c app/migrations/alembic.ini revision --autogenerate -m "YOUR MESSAGE"
alembic -c app/migrations/alembic.ini upgrade head