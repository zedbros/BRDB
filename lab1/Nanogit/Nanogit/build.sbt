val scala3Version = "3.8.1"

lazy val root = project
  .in(file("."))
  .settings(
    name := "numemo",
    version := "0.1.0-SNAPSHOT",
    scalaVersion := scala3Version,
    scalacOptions ++= Seq("-Ximport-suggestion-timeout", "0"),
    libraryDependencies += "redis.clients" % "jedis" % "7.2.0",
    libraryDependencies += "com.lihaoyi" %% "upickle" % "4.1.0",
    // fork in run := true
  )
