sqlite2json
======

This script dumps all* the tables in an sqlite database as json.

## Usage

    sqlite2json sqlitefile.db [--exclude=TABLE]


To dump the sqlite file where iMessages are stored:

    sqlite2json ~/Library/Messages/chat.db

Here is a more useful version of the above example:

    sqlite2json ~/Library/Messages/chat.db | jq -r .message[].text | grep -i loan


\*The script doesn't dump the contents of of the sqlite_master table
