import sns.Simulator
import org.neo4j.driver.GraphDatabase
import org.neo4j.driver.AuthTokens

def handler(query: Simulator.Query): Option[Int] =
  None

@main def Main =
  val s = Simulator(seed = 1337)
  for i <- 0 until 130 do println(s.randomEvent())

  // val dbUri = "neo4j:localhost:7687"
  val dbUri = "neo4j://localhost:7687"
  val dbUser = "neo4j"
  val dbPassword = "beydb-beepr"

  val driver = GraphDatabase.driver(
    dbUri, AuthTokens.basic(dbUser, dbPassword)
    )
  driver.verifyConnectivity()
  print("\n--- YIPPEE --- CONNECTION MADE SUCCESSFULLY !\n")
