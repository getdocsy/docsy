set dotenv-load
set working-directory := 'backend'

# Default recipe to display all available commands
default:
    @just --list

# Run Django development server
serve *args:
    poetry run python src/manage.py runserver {{args}}

# Make and run migrations
migrate:
    poetry run python src/manage.py makemigrations
    poetry run python src/manage.py migrate
