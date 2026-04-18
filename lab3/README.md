# SETUP
### Init
`docker compose -f docker-compose.yaml -f postgres-docker-compose
yaml -f redis-docker-compose.yaml up -d`

### Stop
`docker stop post|mango|red`

### Accessing CLI
#### mongo
`mongosh` ?
#### postgres
idk
#### redis
`docker compose exec cache redis-cli -a password`

# PROJECT
Okay… but we need to select one
- How to choose?
- What do we need to compare?
  - Execution speed of CRUD operators (and to know which one are the relevant in your case)
    - Create
    - Read
    - Update
    - Delete
  - Development speed
    - How long to learn the technology
    - How long to develop something (also depends on how often to change)

#### In short: Comparison.