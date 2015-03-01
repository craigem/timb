# timb - The Internet is My Backup

__USE CASE:__ You have a local git repo that you wish to push to both your own
git server, github and bitbucket.

#### Prerequisites

* A local desktop or laptop with git installed
* Your own server with git installed
* Github account
* Bitbucket account

#### This programme:

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

#### Usage

* If you don't already have one, copy the example netrc to ~/.netrc and replace the example content with your own credentials to GitHub and bitbucket.
* Copy the example timbrc to ~/.timbrc and set the variables to suite your own environment.

## To Do

* Error handling. There's a lot more of it needed.
* Removing all the named repo's with a  "-r" argument.
