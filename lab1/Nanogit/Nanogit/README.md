GROUPE : Axel James John Sebastian

# nanogit

A toy version control system.

## Usage

**`init [uri]`**

Initializes a nanogit repository in the current working directory.

`uri`, if specified, denotes the URI of a Redis server that should serve as a remote store.

**`log`**

Enumerates the commits in the history of the directory, from most recent to oldest.

**`ls`**

Enumerates the files under version control.

**`show file [commit]`**

Shows the contents of `file` at the time of a specific commit.

`commit` denotes the commit at which the contents of the file should be shown. It defaults to the latest commit (i.e., the head) if left unspecified.

**`add file...`**

Adds the specified files to the staging area.

<span style="color:grey">
#### *Explanation*
When adding a file, two things happen:
1. A new temporary file is created called staging in the `.nanogit` folder
2. That same folder is updated with the informations that contains the file that was added as such:
- `{parent_commit_hash, items:{ example.scala:{UUID, modified}}}` where:
    - The `parent` commit hash is set to 0, since this is a temporary state and is not yet added to the final workflow.
    - `items` contains the entierty of files added (modified or not)
    - `UUID` is the directory of the file --> HOW ? => Seems to change each time
    - `modified` is a boolean that determines if the file was simply added with no changes or with changes
    Any file that is added after the fact is added to the staging folder.
</span>
**`commit`**

Commits the changes in the staging area.
<span style="color:grey">
#### *Explanation*
The way each commit is identified, is with a combination of two things:
1. The current commit hash
2. The UUIDs of all the staged files
(No commit will be made, if nothing is staged, or nothing has been added.)

When committed, three things happen:
1. The index file is update, it now conitains the hash of the latest commit.
2. A changes file is added, containing the modifications made.
3. A commit file is created, with a new commit hash that is the staging file.
</span>

#### Notes
THESE ARE PERSONAL NOTES, THE REAL EXPLANATION IS IN THE NEXT SECTION.\
<span style="color:grey">
def combining() creates a new UUID based on two strings of bits.\
|\
but where do the bits come from and what do they represent ?
\
class Item stores the changes of UUID and modified boolean of the file.. have to find where exactly it is called..
same for the commit, except the UUID is the one of the head.. aka last commit hash (I believe), as well as the items described above.
\
What it referes to as index in the code, represents the hash code.
So parseIndex returns the hash of a commit.
\
the @tailrec def loop() in Repository.commit() is where the magic happens. It creates the commit hash that will become the head commit once finished, based on the previous commit hash as well as the UUIDs of all staged files. => we can get the UUID of the staged files because of the nature of the Item class.
\
Each UUID is formed of characters as count: 8-4-4-12.\
The commit hashes are the same format, so are easy to combine using the famous def combining() function. I now think that the term "bits"=section and not bits like 010100 as I initally thought.
</span>

### How the commit hashes and Item UUIDs are created
#### The beginning
To start things off, as mentionned in the description of this lab, when creating a new repository with no commits, it set's the index head (which is the commit hash of the latest commit) to full zeros.\
Each UUID is formed of characters as count: 8-4-4-12 and the commit hashes are the same format, so are later combined to form a unique commit hash each time.\
Once a commit is commited, then the index's head is replaced by the commit's hash.

#### Adding a new file
When we use the `add` command on a file, we enter the staging section. The command will create a new `case class Item`. This class posses UUID to identify it, as well as a modified boolean which confirms or denies any modiciations made to the file, ?since the last commit?.\

The way the Item's UUID is created is via an automatic `java.util.UUID` function if and only if the same exact file is not already in the staging file.\
The staging file contains all the added files.

Next, the file name is retrieved and with the newly created Item, call storeCommit() but the name it is given is "staging". This part inserts

`{example.scala:{UUID, modified}` into the staging file `items:` section as show below

`{parent_commit_hash, items:{ example.scala:{UUID, modified}}}`,

where
`example.scala` is the file name with the `Item` with it's attributes `UUID` and `modified`, and since this is staging commit, the `parent_commit_hash` is all zeros.

#### Commiting
Once we have added all the files we wanted, we run `commit`.

This calls parseStating(), which calls parseCommit() but with name = "staging", which return the entire line of data in the staging file. From this method call we are now going to create the new commit hash.

Each commit hash is a merge between the current commit hash (remember that we still haven't full comitted since the code is running (intermediate stage)) and the UUIDs of all the items in the staging file.

This is done through a tail recursive loop which at each step checks if there are any items left in it's search. If there are, then it isolates the name-Item combo and stores it as a progress monitor. It then calls the recursive function but passed the UUID into the hash.combining() function which executes in the recursive function call.

`combining()` is very important as it merges two UUID's together to form one. It goes through each character and works in bit format, combining the first and second UUID with a prime number and a combination of complexe mathematical operations, that forms one code.

Once there are no more items left, then it returns the hash and all the items list.

Finally storeCommit is called with the name as the returned hash, current commit hash (=> become the parent hash which represents the previous commit relative to this one so a linear history is automatically created) and items, so we obtain a new individual file named after the hash, with the same file type as "staged" but with the head hash or parent hash changing from all zeros, to the current commit hash, followd by the items as seen before.

Then the index file is updated with the new commit hash, and the staging file is deleted.

All done.

