### Social Network API

## To build docker
docker-compose build

## To run docker containers
docker-compose up

## To down the docker containers
docker-compose down

## Necessary steps :-
'''
docker-compose run social_network bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
'''


## List of endpoints:-
1. User Signup
2. User Login
3. User Search
4. Send Friend Request (Includes rate limiting)
5. Accept/Reject Friend Request
6. List Friends (Accepted only)
7. List Pending Friend Requests
