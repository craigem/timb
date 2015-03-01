#!/usr/bin/env python
'''
USE CASE:
You have a local git repo that you wish to push to both your own git server,
github and bitbucket.

This script
* Reads your local ~/.netrc
* Gets repo name and description from arguments
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
'''

import ConfigParser
import os
import sys
from git import Repo
from shutil import copyfile
from paramiko import client
from paramiko import AutoAddPolicy
from textwrap import dedent
import commands
import requests
import json

# Get HOME
HOME = os.getenv('HOME')
RCFILE = ("%s/.gitweb_repo_build.rc" % HOME)

# Read the variables from the local config file
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(RCFILE)
GITDIR = CONFIG.get("grb", "GITDIR")
GITHUBUSER = CONFIG.get("grb", "GITHUBUSER")
BITBUCKETUSER = CONFIG.get("grb", "BITBUCKETUSER")
GITSERVER = CONFIG.get("grb", "GITSERVER")
GITREMOTEDIR = CONFIG.get("grb", "GITREMOTEDIR")
LICENSE = CONFIG.get("grb", "LICENSE")
# Set the repo directory:
REPONAME = sys.argv[1]
REPODIR = GITDIR + "/" + REPONAME
# Set the repo description
DESCRIPTION = sys.argv[2]
# Set the remote values
REMOTES = dedent("""
    [remote "github"]
    url = git@github.com:%s/%s.git
    fetch = +refs/heads/*:refs/remotes/github/*
    autopush = true

    [remote "bitbucket"]
    url = git@bitbucket.org:%s/%s.git
    fetch = +refs/heads/*:refs/remotes/bitbucket/*
    autopush = true""" % (
        GITHUBUSER, REPONAME, BITBUCKETUSER, REPONAME))
HOOK = dedent("""
    #!/bin/bash
    for remote in $(git remote); do
        if [ "$(git config "remote.${remote}.autopush")" = "true" ]; then
            git push --all "$remote"
        fi
    done""")


def localrepo():
    ''' Creates and initialises the git repoa.'''
    if not os.path.exists(REPODIR):
        # Initialise the repo
        Repo.init(REPODIR)

        # Add the description
        description = "%s/.git/description" % REPODIR
        with open(description, "w") as text_file:
            text_file.write(DESCRIPTION)

        # Add the LICENSE file
        dst = "%s/LICENSE" % REPODIR
        copyfile(LICENSE, dst)
        repo = Repo.init(REPODIR)
        repo.index.add([dst])
        repo.index.commit("Added LICENSE.")

        # Add the README file
        readme = "%s/README" % REPODIR
        with open(readme, "w") as text_file:
            text_file.write(
                "# %s \nThis is the initial README for the %s git repo."
                % (REPONAME, REPONAME))
        repo.index.add([readme])
        repo.index.commit("Added README.")

        # Adds the remote git repo as origin
        remoteurl = "ssh://%s%s/%s" % (GITSERVER, GITREMOTEDIR, REPONAME)
        repo.create_remote('origin', remoteurl)

        # Push the initial content
        print "Pushing the initial content."
        origin = repo.remotes.origin
        origin.push("--all")

    else:
        print "Directory %s already exists" % REPODIR


def remoterepo():
    '''Builds a git repo hosted via remote git server'''
    # Throw in an if exists here as per localrepo
    sshclient = client.SSHClient()
    # sftpclient = sftp_file.SFTPFile(sftp, handle, mode='r', bufsize=-1)
    sshclient.load_system_host_keys()
    sshclient.set_missing_host_key_policy(AutoAddPolicy())
    sshclient.connect(GITSERVER)
    # rexists(sftpclient, "%s/%s" % (GITREMOTEDIR, REPONAME))
    print "Creating %s on %s" % (REPONAME, GITSERVER)
    sshclient.exec_command('mkdir %s/%s' % (GITREMOTEDIR, REPONAME))
    sshclient.exec_command('git init --bare %s/%s' % (GITREMOTEDIR, REPONAME))
    sshclient.exec_command(
        'echo %s > %s/%s/description' % (DESCRIPTION, GITREMOTEDIR, REPONAME))
    # Adds a remote for github and bitbucket.
    sshclient.exec_command(
        'echo -e %s >> %s/%s/config' % (
            commands.mkarg(REMOTES), GITREMOTEDIR, REPONAME))
    # Adds a remote git hook for automatically pushing to configured remotes.
    sshclient.exec_command(
        'echo -e %s >> %s/%s/hooks/post-receive' % (
            commands.mkarg(HOOK), GITREMOTEDIR, REPONAME))
    sshclient.exec_command(
        'chmod u+x %s/%s/hooks/post-receive' % (
            GITREMOTEDIR, REPONAME))


def socialrepos():
    '''Creates a repo at Github and Bitbucket.'''
    print "Creating the repo at Github"
    payload = json.dumps({'name': REPONAME, 'description': DESCRIPTION})
    req = requests.post(
        'https://api.github.com/user/repos', payload)
    print "Creating the repo at Bitbucket"
    payload = json.dumps({"description": "%s" % DESCRIPTION})
    req = requests.post(
        'https://api.bitbucket.org/2.0/repositories/%s/%s' %
        (BITBUCKETUSER, REPONAME), payload)
    # Description not working for Bitbucket...


def main():
    '''Run the main program'''
    remoterepo()
    socialrepos()
    localrepo()


main()
