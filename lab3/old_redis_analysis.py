import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Set and retrieve string values using SET and GET commands
# r.set('foo', 'bar')
r.get('foo')

# # Store and retrieve hash data structures using HSET and HGETALL
# r.hset('user-session:123', mapping={
#     'name': 'John',
#     "surname": 'Smith',
#     "company": 'Redis',
#     "age": 29
# })
# r.hgetall('user-session:123')

print("REDIS REQUEST DONE")

# # Close redis client
# r.close()