# Socialify Service

Simple social network REST API

## Prerequisites

- Docker
- docker-compose

## Get started

1. Create `.env` file at the root of the project using `.env.sample` file (mostly you need to fill in `JWT_ENCODE_KEY` env variable);
2. Run Docker containers using following command:

```sh
$ docker-compose up -d
```

## Usage

1. First create user using `POST /users/` endpoint;

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "test@example.com",
  "password": "password"
}'
```

2. Login using `POST /login/` endpoint;

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/login/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "test@example.com",
  "password": "password"
}'
```

Output:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NzM0NzIyMzZ9.ng9d_rLoKzgm76eVO-ISVOgAfyXJNT_qog-tVgZ8ugg",
  "token_type": "bearer"
}
```

3. Use API token from `login` endpoint response in other endpoints (e.g. `POST /posts/`) via `Authorization` header;

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/posts/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {API_TOKEN_HERE}' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "post1",
  "content": "post1 content",
  "published": true
}'
```

## Technologies

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- OAuth 2.0 and JWTokens
