# Movie Casting API

This is a RESTful API for managing movies and actors. The API supports authentication using Auth0 and performs CRUD operations on the database.

## Getting Started

### Prerequisites
- Python 3.8+
- Flask
- PostgreSQL
- Auth0 account

### Installation
1. Clone this repository:
   ```sh
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Create and activate a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Flask-related environment variables should be in a `.flaskenv` file.
   - Database and Auth0 configuration should be stored in a `.env` file (not included in the  
     repository). All variable with sample values are as follows.

    ```sh
    # Database Configuration
    DATABASE_NAME=casting_agency
    TEST_DATABASE_NAME=test_casting_agency
    DATABASE_URL=postgresql://postgre:pass1234@localhost:5432/

    # Auth0 Configuration - Must for running on Render (Replace with actual values)
    AUTH0_DOMAIN=dev-test.auth0.com
    API_AUDIENCE=https://casting-agency/api
    ALGORITHMS=RS256

    # Logging
    LOG_DIR=backend/logs

    # Tokens for testing only (Replace with actual values - can be obtained by using auth0 URL for your API)
    DIRECTOR_TOKEN=eqwer
    PRODUCER_TOKEN=1234
    ASSISTANT_TOKEN=abcd
    ```


### Running the application
To start the PostgreSQL, run:
```sh
pg_ctl -D /opt/homebrew/var/postgres start
```

To start the Flask application, run:
```sh
flask run
```
This will start the API server using the configuration from `.flaskenv`.

### Test the application
to run tests, run:
```sh
python -m unittest backend/src/test_flask.py -v
```

## API Endpoints

### Health Check
#### `GET /`
**Response:**
```json
{
  "success": true,
  "health": true
}
```

### Actors
#### `GET /actors`
Requires `get:actors` permission.
```sh
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:5000/actors
```

#### `POST /actors`
Requires `post:actors` permission.
```sh
curl -X POST http://localhost:5000/actors \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 35, "gender": "male"}'
```

#### `PATCH /actors/<id>`
Requires `patch:actors` permission.
```sh
curl -X PATCH http://localhost:5000/actors/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"age": 40}'
```

#### `DELETE /actors/<id>`
Requires `delete:actors` permission.
```sh
curl -X DELETE http://localhost:5000/actors/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Movies
#### `GET /movies`
Requires `get:movies` permission.
```sh
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://localhost:5000/movies
```

#### `POST /movies`
Requires `post:movies` permission.
```sh
curl -X POST http://localhost:5000/movies \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Inception", "release_date": "2010-07-16"}'
```

#### `PATCH /movies/<id>`
Requires `patch:movies` permission.
```sh
curl -X PATCH http://localhost:5000/movies/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "The Matrix"}'
```

#### `DELETE /movies/<id>`
Requires `delete:movies` permission.
```sh
curl -X DELETE http://localhost:5000/movies/1 \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Error Handling
Errors are returned as JSON objects in the following format:
```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```
Common error codes:
- `400`: Bad request
- `404`: Resource not found
- `422`: Unprocessable entity
- `500`: Internal server error

## Authentication
- This API uses Auth0 for authentication. Each request requiring authentication must include a valid `Authorization: Bearer <ACCESS_TOKEN>` header.
- There are three roles as per casting agency project description.

## Logging
Logs are stored in the `logs/execution.log` file.



