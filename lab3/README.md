# SETUP
### Init
`docker compose -f docker-compose.yaml -f postgres-docker-compose
yaml -f redis-docker-compose.yaml up -d`

### Run
You can easily run each test by choosing your amount of records to insert and test on (n=...) and run the python file.

### Stop
`docker stop post|mango|red`

# PROJECT


### Fairness
To ensure fairness, I made sure:
- All databases run in docker
- Only one docker was running at a time when testing
- My system's power profile remained the same

There is however, one critical flaw. The Postgres database test is async. This is because I was unable to get `psycopg, psycopg2 and pg8000` working for the life of me.