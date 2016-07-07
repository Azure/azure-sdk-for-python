#!/bin/sh
FILE=~/.gem/credentials
chmod 0600 ${FILE} > ${FILE}
echo ":azure: ${KEY}" > ${FILE}
bundle install
bundle exec rake arm:release[azure]
rm ${FILE}
