import sqlite3
import sys
import json
import base64

def main():
    exclude_tables = []

    try:
        for i, token in enumerate(sys.argv):
            if i < 1:
                continue
            if i == 1:
                db_file = token
            if i > 1:
                exclude_tables.append(token.split('--exclude=')[1])
        assert(db_file)
    except (IndexError, NameError):
        show_usage()
        sys.exit(127)

    exclude_tables = set(exclude_tables)
    print sqlite2json(
        db_file=db_file,
        exclude_tables=exclude_tables
    )

def show_usage():
    print 'Usage:\n\tsqlite2json sqlitefile.db --exclude=table_name --exclude=table_name'

def sqlite2json(exclude_tables=None,db_file=None):
    # Make sure blobs are base64 encoded
    sqlite3.register_converter('BLOB', base64.b64encode)

    conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    return json.dumps(get_tables(cursor))

def get_table_list(cursor, exclude_tables=set([])):
    cursor.execute('SELECT * FROM main.sqlite_master WHERE type="table"')
    return set(row[1] for row in cursor.fetchall()) - exclude_tables

def get_column_names(cursor, table_name):
    cursor.execute('SELECT * FROM %s' % table_name)
    return [c[0] for c in cursor.description]

def get_table(cursor, table_name):
    column_names = get_column_names(cursor,table_name)
    cursor.execute('SELECT * FROM main.%s' % table_name)
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]

def get_tables(cursor):
    table_list = get_table_list(cursor)
    output = {}
    for table_name in table_list:
        output[table_name] = get_table(cursor, table_name)
    return output

if __name__ == "__main__":
    main()
