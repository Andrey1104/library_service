# Library service API

API service for borrowing books and library management written on DRF

API allow users to create profiles, follow other users, create and retrieve posts, messages and events, manage likes and comments, and perform basic social media actions.

Technologies
Django Rest Framework
Celery + Redis for scheduled borrowing notification
Postgres
Docker

## Run with Docker
Docker must be already installed

Copy .env-sample to .env and populate with all required data.

docker-compose up --build 
Note: superuser is created automatically with .env info if no users exist in database.

Getting access🔓
Creating user: /api/user/register/

Getting access token: /api/user/token/


### Features ⭐
- JWT authentication (with logout function)
- Admin panel via /admin/
- Documentation via /api/doc/swagger/
- Extended payment system for borrowing with stripe
- CRUD operations for books
- Retrieving borrowings by user
- Scheduled borrowing notification and payment status
- Auto superuser creation on first launch
