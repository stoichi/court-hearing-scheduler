# court-hearing-scheduler

# Overview
A simple mockup of what the scheduling part of a system for booking court hearings could be. It allows for a clerk to create hearings that contain a list of Participants.

# Assumptions
- The system currently does not have accounts for booking the hearings so anyone can go to the url unauthenticated
- There is only one court room so bookings can't overlap
- Hearings are scheduled on a per-day basis 
- Any number of people can join the meeting and no specific roles are required
- Only considers the booking part, there is no part for the joining the hearing

# Shortcuts
- Using whitenoise for static file delivery for docker
- Using inbuilt signals instead of a task scheduler
- Envvars are set directly in docker compose rather than a secret manager
- Using pico css for most css styling
- Seeding some user data into the database for easier demonstration of the system via django management command
- New hearings are polled every 30 seconds through HTMX

# Implementation details
- Using Django User model as the core Participant model to allow for future improvements and Django permission integrations
- Forms and Templates for delivering the Frontend to allow for easy creation and validation of Model data
- DRF for exposing the external API using ModelViewSets to reduce boilerplate code
- Simple validation checks for correct data, e.g. only future dates and checks for no overlapping hearings
- Simple tests for checking core functionality
- Added bonus feature of mocking how users could be emailed when their hearings are modified, this is currently just printed to the log as the users do not have real emails but shows potential functionality
- Optimised queries to reduce database polls
- Uses Gunicorn to run in Docker instead of development server
- Uses UV as a Python version and package manger

# Future improvements
- Authentication/Authorization support
- Multiple user support
- SSE or Websockets for updating data
- Enforce that specific roles are required for a hearing to take place
- Task Scheduler for sending emails
- Secrets manager for storing deployment environment variables
- General design and user interaction
- Show past hearings and current date/time
- Further tests to check edge cases and non-happy paths
- Further APIs such as /users/hearings
- Django logging improvements

# Running in Docker
- Docker files can be found in [/docker](docker)
- To run:
  ``` shell
  cd docker
  docker compose up -d
  ```
- Server is started on port 8000
- Access locally http://localhost:8000
- Swagger docs can be found at http://localhost:8000/api/schema/swagger-ui/

> Pre-made admin user can be used for demo purposes with 
>  - Username: admin 
>  - Password: admin

# Running Tests
- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Sync dependencies and run the tests:
  ``` shell
  uv sync
  source .venv/bin/activate # On Windows: .venv\Scripts\activate
  cd src
  python manage.py test
  ```