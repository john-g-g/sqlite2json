# lite2j -- sqlite to json export utiilty

This script dumps all* the tables in an sqlite database as json.

## Usage

    lite2j sqlitefile.db [--exclude=TABLE]


To dump the sqlite file where iMessages are stored:

    lite2j ~/Library/Messages/chat.db

Here is a more useful version of the above example:

    lite2j ~/Library/Messages/chat.db | jq -r .message[].text | grep -i loan


\*The script doesn't dump the contents of of the sqlite_master table 

