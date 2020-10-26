#!/bin/sh

git push origin master
git push origin master --tags

git push heroku master
heroku ps:scale jacob=1
