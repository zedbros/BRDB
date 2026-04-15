package nanogit

import redis.clients.jedis.RedisClient

/** Returns the result of calling `action` with a redis client created with the given `url`.
 *
 *  @param url The Redis URI string identifying the server to which the client should connect. The
 *    URI must be in the format `redis[s]://[[user][:password]@]host[:port][/database]`.
 *  @param action A closure that accepts a redis client as unique argument. The client is valid
 *    only during the execution of the closure and closed automatically.
 *
 *  @return The result of `action`.
 */
def withRedisClient[T](url: String)(action: RedisClient => T): T =
  val client = RedisClient.create(url)
  val result = action(client)
  client.close()
  result
