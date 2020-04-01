#!/bin/bash

# Fail out on an error
set -e

# CD into docs, make them. If you're not using Sphinx, you'll probably
# have a different build script.
make -C docs/ clean html

# Move the docs to the top-level directory, stash for checkout
mv docs/build/html/ .

# The html/ directory will stay there when we stash
git stash --include-untracked

# Checkout our gh-pages branch, remove everything but .git
git checkout gh-pages
git pull origin gh-pages

# Make sure to set the credentials! You'll need these environment vars
# set in the "Environment Variables" section in Circle CI
git config --global user.email "$GH_EMAIL" > /dev/null 2>&1
git config --global user.name "$GH_NAME" > /dev/null 2>&1

# Remove all files that are not in the .git dir
git rm -rf .
git clean -fxd

# We need this empty file for git not to try to build a jekyll project.
# If your project *is* Jekyll, then this doesn't apply to you...
touch .nojekyll
git stash apply
mv html/* .
rm -r html/

# Add everything, get ready for commit. 
git add --all
git commit -m "Publishing Updated Documentation" || true

# We have to re-add the origin with the GH_TOKEN credentials. You
# will need this SSH key in your environment variables.
# Make sure you change the <project>.git pattern at the end!
git remote rm origin
git remote add origin https://"$GH_NAME":"$GH_TOKEN"@github.com/"$GH_NAME"/AkaNamen-Bot.git

# NOW we should be able to push it
git push origin gh-pages || true
