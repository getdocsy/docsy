# Default recipe to display all available commands
default:
    @just --list

# Run Django development server
serve *args:
    poetry run python manage.py runserver {{args}}

# Make and run migrations
migrate:
    poetry run python manage.py makemigrations
    poetry run python manage.py migrate