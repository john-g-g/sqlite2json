#!/usr/bin/env python

import re
import bisect
import pprint


def get_table_list(cursor, exclude_tables=set()):
    cursor.execute('SELECT * FROM main.sqlite_master WHERE type="table"')
    return set(row[1] for row in cursor.fetchall()) - exclude_tables


def get_tables(cursor, exclude_tables):
    table_list = get_table_list(cursor, exclude_tables=exclude_tables)
    return {table_name: get_table(cursor, table_name)
            for table_name in table_list}


def get_tables_info(cursor):
    cursor.execute('SELECT * FROM main.sqlite_master WHERE type="table"')
    return cursor.fetchall()


def get_column_names(cursor, table_name):
    cursor.execute('SELECT * FROM %s' % table_name)
    return [c[0] for c in cursor.description]


def get_table(cursor, table_name):
    column_names = get_column_names(cursor, table_name)
    cursor.execute('SELECT * FROM main.%s' % table_name)
    return [dict(zip(column_names, row)) for row in cursor.fetchall()]


def get_tables_data(cursor):
    table_list = get_table_list(cursor)
    return {
        table_name: get_table(cursor, table_name) for
        table_name in table_list}


def build_table_map(cursor, exclude_tables=set()):
    table_list = get_tables_info(cursor)
    table_names = [table['tbl_name'] for table in table_list]
    tables = dict()
    for table in table_list:
        name = table['tbl_name']
        sql = table['sql']
        columns = get_column_names(cursor, name)
        column_defs = get_column_defs(sql)
        ref_indexes = []
        child_column_indexes = []
        parent_table_indexes = []
        parent_table_ref_map = {}
        child_column_ref_map = {}
        parent_column_ref_map = {}
        if column_defs:
            ref_indexes = find_keyword_indexes(
                column_defs, keyword='REFERENCES')
            child_column_indexes = find_indexes(column_defs, columns)
            child_column_ref_map = {ref: find_rightmost_lt_index(
                child_column_indexes, ref) for ref in ref_indexes}
            parent_table_indexes = find_indexes(column_defs, table_names)
            parent_table_ref_map = {ref: find_leftmost_gt_index(
                parent_table_indexes, ref) for ref in ref_indexes}
            parent_column_ref_map = {ref: find_parent_column_for_ref(
                column_defs,
                ref,
                parent_table_ref_map, cursor) for ref in ref_indexes}

        tables[name] = dict(sql=sql,
                            columns=columns,
                            column_defs=column_defs,
                            ref_indexes=ref_indexes,
                            child_column_ref_map=child_column_ref_map,
                            parent_table_ref_map=parent_table_ref_map,
                            parent_table_indexes=parent_table_indexes,
                            child_column_indexes=child_column_indexes,
                            parent_column_ref_map=parent_column_ref_map)
    return tables


def get_column_defs(sql):
    columns_pattern = r'^CREATE\s+TABLE\s+\w+\s+\(\s?(?P<column_defs>.*)\)$'
    matches = re.match(columns_pattern, sql, flags=re.IGNORECASE)
    if matches:
        return matches.group('column_defs')
    else:
        return None


def find_keyword_indexes(text, keyword=None):
    return [m.start() for m in re.finditer(keyword, text, flags=re.IGNORECASE)]


def find_indexes(text, keywords):
    return {keyword: find_keyword_indexes(text, keyword=keyword)
            for keyword in keywords}


def find_rightmost_lt_index(indexes, ref_index):
    inverted = build_inverted_index(indexes)
    idx = find_lt(sorted(inverted.keys()), ref_index)
    return inverted[idx]


def find_leftmost_gt_index(indexes, ref_index):
    inverted = build_inverted_index(indexes)
    idx = find_gt(sorted(inverted.keys()), ref_index)
    return inverted[idx]


def find_parent_column_for_ref(text, ref_index, table_name_ref_map, cursor):
    referenced_table = table_name_ref_map[ref_index]
    columns = get_column_names(cursor, referenced_table)
    child_column_indexes = find_indexes(text, columns)
    return find_leftmost_gt_index(child_column_indexes, ref_index)


def build_inverted_index(indexes):
    inverted = dict()
    for key, value_list in indexes.iteritems():
        for value in value_list:
            inverted[value] = key
    return inverted


def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect.bisect_left(a, x)
    if i:
        return a[i - 1]
    raise ValueError


def find_gt(a, x):
    'Find leftmost value greater than x'
    i = bisect.bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

# debugging stuff


def print_tables_info(tables):
    for name, t in tables.iteritems():
        if len(t['ref_indexes']) > 0:
            pprint.pprint(tables)


def print_references(tables):
    for name, t in tables.iteritems():
        for ref in t['ref_indexes']:
            col = t['child_column_ref_map'][ref]
            tbl = t['parent_table_ref_map'][ref]
            parent_column = t['parent_column_ref_map'][ref]
            print '%s.%s ----> %s.%s' % (name, col, tbl, parent_column)
