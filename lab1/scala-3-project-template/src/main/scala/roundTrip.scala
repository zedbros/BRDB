import redis.clients.jedis.RedisClient

@main def RoundTrip(): Unit = 
    val db = RedisClient.create("redis://localhost:6379")
    db.set("foo", "bar")
    println(db.get("foo"))
    db.close()