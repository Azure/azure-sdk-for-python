#!/bin/bash -e

git checkout master
git fetch upstream
git merge upstream/master
