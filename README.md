# timb - The Internet is my backup

USE CASE:
You have a local git repo that you wish to push to both your own git server,
github and bitbucket.

This script
* Reads your local ~/.netrc
* Gets a repo name and description from arguments
* Builds a git repo locally
* Adds a README.md and a LICENCE. Commits the changes.
* Builds a git repo hosted via your remote git server
* Adds a git hook for automatically pushing to configured remotes from your
remote
* Adds a remote for github on your remote server.
* Adds a remote for bitbucket on your remote server.
* Creates a repo at GitHub.
* Creates a repo at bitbucket.
* Pushes to remote.
