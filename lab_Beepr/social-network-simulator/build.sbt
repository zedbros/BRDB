val scala3Version = "3.8.1"

lazy val root = project
  .in(file("."))
  .settings(
    name := "social-network-simulator",
    version := "0.1.0-SNAPSHOT",
    scalaVersion := scala3Version,
    libraryDependencies += "org.scalameta" %% "munit" % "1.3.0" % Test,
    libraryDependencies += "org.neo4j.driver" % "neo4j-java-driver" % "6.0.5")
