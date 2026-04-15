package nanogit

import java.nio.charset.StandardCharsets
import java.nio.file.{Files, NoSuchFileException, Path, Paths}
import java.util.UUID

import scala.annotation.tailrec
import scala.collection.View
import scala.util.{Try, Success, Failure}

import upickle.default as json

extension (self: Path)

  /** Returns `true` iff `self` is a prefix of `other`. */
  def contains(other: Path): Boolean =
    val a = self.normalize().toAbsolutePath.iterator()
    val b = other.normalize().toAbsolutePath.iterator()
    def loop(): Boolean =
      !a.hasNext() || (b.hasNext() && a.next().equals(b.next()) && loop())
    loop()

extension (self: UUID)

  /** The 64 lowest bits of `self`. */
  private def lower: Long =
    self.getLeastSignificantBits()

  /** The 64 highest bits of `self`. */
  private def upper: Long =
    self.getMostSignificantBits()

  /** Returns `true` iff all bits in `self` are zeroed. */
  def isZero: Boolean =
    (self.lower == 0) && (self.upper == 0)

  /** Returns a new UUID combining the bits of `self` and `other`. */
  def combining(other: UUID): UUID =
    val prime = 0x100000001b3L
    @tailrec def fnv(i: Int, n: Long, h: Long): Long =
      if i == 64 then h else fnv(i + 8, n, (h * prime) ^ ((n >> i) & 0xff))
    UUID(
      fnv(0, other.upper, self.lower),
      fnv(0, fnv(0, other.lower, self.lower), self.upper))

/** The representation of a file's contents in a single commit.. */
case class Item(uuid: UUID, modified: Boolean) derives json.ReadWriter

/** A map from file names to their contents. */
case class Commit(parent: UUID, items: Map[String, Item]) derives json.ReadWriter

object Commit:

  /** Returns an empty commit. */
  def empty: Commit =
    Commit(UUID(0, 0), Map.empty)

/** The contents of a repository. */
case class Repository(remote: String, head: UUID) derives json.ReadWriter

object Repository:

  /** Throws a runtime error diagnosed by `message` iff `condition` is `false`. */
  private def guard(condition: Boolean, message: => String): Unit =
    if !condition then throw RuntimeException(message)

  /** Returns `true` iff `root` is the root of a nanogit repository. */
  private def isRepository(root: String): Boolean =
    Files.exists(Paths.get(root, ".nanogit", "index"))




  /** Returns a path to the metadata identified by `components` in the repository at `root`. */
  private def path(root: String, components: String*): Path =
    Paths.get(Paths.get(root, ".nanogit").toString, components*)




  /** Returns the index of the repository at `root`. */
  private def parseIndex(root: String): Repository =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    val data = Files.readString(path(root, "index"), StandardCharsets.UTF_8)
    json.read[Repository](data)

  /** Returns the contents of the commit with the specified `name` in the repository at `root`. */
  private def parseCommit(root: String, name: String): Commit =
    val data = Files.readString(path(root, name), StandardCharsets.UTF_8)
    json.read[Commit](data)

  /** Returns the contents of the staging area in the repository at `root`. */
  private def parseStaging(root: String): Commit =
    try
      parseCommit(root, "staging")
    catch
      case e: NoSuchFileException => Commit.empty




  /** Saves the given index to disk in the repository at `root`. */
  private def storeIndex(root: String, value: Repository): Unit =
    val writer = Files.newBufferedWriter(path(root, "index"))
    writer.write(json.write(value))
    writer.close()

  /** Saves the given commit to disk under the given `name` in the repository at `root`. */
  private def storeCommit(root: String, name: String, value: Commit): Unit =
    val writer = Files.newBufferedWriter(path(root, name))
    writer.write(json.write(value))
    writer.close()

  /** Clears the staging area of the repository at `root`. */
  private def clearStaging(root: String): Unit =
    Files.delete(path(root, "staging"))




  /** Initializes a nanogit repository at `root` . */
  def initialize(root: String, arguments: Seq[String]): Unit =
    guard(arguments.length < 2, "command takes at most 1 argument")

    Files.createDirectories(path(root))
    val remote = arguments.headOption.getOrElse("redis://localhost:6379")
    storeIndex(root, Repository(remote, UUID(0, 0)))

  /** Lists the commits in the repository at `root`. */
  def log(root: String, arguments: Seq[String]): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    guard(arguments.isEmpty, "command takes no argument")

    @tailrec def loop(name: UUID): Unit =
      if name.isZero then () else
        println(name.toString)
        loop(parseCommit(root, name.toString).parent)
    loop(parseIndex(root).head)

  /** Lists the files versioned in the repository at `root`. */
  def list(root: String, arguments: Seq[String]): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    guard(arguments.isEmpty, "command takes no argument")

    val self = parseIndex(root)
    val head = if self.head.isZero then Commit.empty else parseCommit(root, self.head.toString)
    head.items.keys.toSeq.sorted.foreach(println)

  /** Shows a file versioned in the repository ar `root`. */
  def show(root: String, arguments: Seq[String]): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    guard(!arguments.isEmpty, "expected input")

    // Get the commit at which the contents of the file should be shown.
    val patch = if arguments.length > 1 then
      parseCommit(root, arguments(1))
    else
      val self = parseIndex(root)
      if self.head.isZero then Commit.empty else parseCommit(root, self.head.toString)

    // Compute the path of the file relative to the root of the repository.
    val prefix = Paths.get(root).toAbsolutePath()
    val u = prefix.relativize(Paths.get(arguments(0)).toAbsolutePath())

    // Locate and show the file contents.
    patch.items.get(u.toString) match
      case Some(Item(id, modified)) =>
        if modified then
          println(Files.readString(path(root, id.toString), StandardCharsets.UTF_8))
        else
          show(root, List(u.toString, patch.parent.toString))
      case None =>
        throw RuntimeException(s"'${u}' is not versioned")




  /** Adds the given files to the staging area of the repository at `root`. */
  def add(root: String, files: Seq[String]): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")

    val prefix = Paths.get(root).toAbsolutePath()
    val result = files.foldLeft(parseStaging(root)) { (patch, f) =>
      // Make sure the file is in the repository.
      val u = Paths.get(f).toAbsolutePath()
      guard(prefix.contains(u), s"'${f}' is outside the repository")

      // Don't update anything if the file was already there.
      val k = prefix.relativize(u).toString
      patch.items.get(k) match
        case Some(Item(_, true)) => patch
        case _ => patch.copy(items = patch.items.updated(k, Item(UUID.randomUUID, true))) // k is name of the file
    }
    storeCommit(root, "staging", result) // When case_ => then result = patch.copy(...)

  /** Commits the file in the staging area of the repository at `root`. */
  def commit(root: String, arguments: Seq[String]): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    guard(arguments.isEmpty, "command takes no argument")

    val patch = parseStaging(root) // all the staging data
    if patch.items.isEmpty then
      // Nothing to do if the staging area is empty.
      System.err.println("no change")

    else
      // Load the parent commit, if any.
      val self = parseIndex(root)
      val base = if self.head.isZero then Commit.empty else parseCommit(root, self.head.toString)

      // Save the files that have been staged and compute the hash of the new commit based on the
      // parent commit and the identities of all staged files.
      @tailrec def loop(
          fresh: Map[String, Item], previous: Map[String, Item], keys: View[String],
          hash: UUID, merged: Map[String, Item]
      ): (UUID, Map[String, Item]) = keys.headOption match
        case Some(source) => fresh.get(source) match
          case Some(item) =>
            // The item is in in the staging area.
            Files.copy(Paths.get(source), path(root, item.uuid.toString))
            val ms = merged.updated(source, item)
            loop(fresh, previous, keys.tail, hash.combining(item.uuid), ms)
          case None =>
            // The item is not in the staging area.
            val ms = merged.updated(source, previous(source).copy(modified = false))
            loop(fresh, previous, keys.tail, hash, ms)
        case None =>
          (hash, merged)

      val (hash, items) = loop(
        patch.items, base.items, patch.items.keys.concat(base.items.keys).view,
        self.head, Map.empty)

      // Save the new commit, clear the staging area, and update the index.
      storeCommit(root, hash.toString, Commit(self.head, items))
      storeIndex(root, self.copy(head = hash))
      clearStaging(root)



  def push(root: String): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")

    val self = parseIndex(root)               // on va chercher dans le fichier index pour trouver l'url du remote
    val db = RedisClient.create(self.remote)  // avec ce remote, on crée un client Redis pour pouvoir communiquer avec le serveur Redis
    val remoteHead = db.get("head")           // Récupère le head actuel sur Redis (null si Redis est vide)
    if remoteHead == self.head.toString then  // Si le remote est déjà à jour, rien à faire
      println("already up to date")
      db.close()
    else
      var current = self.head
      while !current.isZero && current.toString != remoteHead do  // on remonte la racine tant que ça match pas avec le head du remote
        val commit = parseCommit(root, current.toString)          // on lit le commit actuel à partir du fichier local ==> commit
        db.set(current.toString, json.write(commit))              // on copie le commit actuel vers le remote, current c'est l'identifiant du commit , commit c'est
        
        commit.items.foreach { case (file, item) =>               // maintenant on copie le contenu du commit qu'on vient de copier
          if item.modified then
            val content

        current = commit.parent                                   // on met à jour current pour remonter d'un commit en arrière   

    System.err.println("not implemented")

  def pull(root: String): Unit =
    guard(isRepository(root), s"no nanogit repository at ${Paths.get(".")}")
    System.err.println("not implemented")


  // DEMANDER le head au serveur
  // Quatres cas de figure:
  // 1. le head du serveur est égal au head local ==> rien à faire
  // 2. le head du serveur est un commit qui n'existe pas localement ==>
  //    on remonte la racine du serveur tant que le head du serveur n'est pas égal à un commit local
  //    pour chaque commit qu'on remonte, on le copie localement
  // 3. le head du serveur est un commit qui existe localement mais qui n'est
  //    pas le head local ==> on remonte la racine du serveur tant que le head du serveur n'est pas égal au head local
  //    pour chaque commit qu'on remonte, on le copie localement
  // 4. le head du serveur est un commit qui existe localement et qui est égal
  //    au head local ==> on met à jour le head local pour qu'il soit égal au head du serveur

end Repository

@main def Main(command: String, arguments: String*) =
  val root = "."
  try command match
    case "init" =>
      Repository.initialize(root, arguments)
    case "log" =>
      Repository.log(root, arguments)
    case "ls" =>
      Repository.list(root, arguments)
    case "show" =>
      Repository.show(root, arguments)
    case "add" =>
      Repository.add(root, arguments)
    case "commit" =>
      Repository.commit(root, arguments)
    case other =>
      throw RuntimeException(s"unknown command '${other}'")
  catch case e => System.err.println(s"error: ${e.toString}")
