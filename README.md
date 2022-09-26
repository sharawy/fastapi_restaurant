# fastapi_restaurant
Restaurant reservation system 
# How to run
- ``docker-compose up --build`` 
- go to http://localhost:8000/docs

# how to use
User the admin creds to obtain authentication token using the v1/users/login api:
```
{
  "e_number": 1000,
  "password": "admin1234"
} 
```
Use the token to make requests as below

![Alt text](example.png?raw=true "Title")


## License

This project is licensed under the terms of the MIT license.
