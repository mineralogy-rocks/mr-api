# -*- coding: utf-8 -*-
from django.db import connection
from io import StringIO
from django.conf import settings
import os
import re


# get sql file
def run_sql_file(filename):
    def load_data_from_sql(app, schema_editor):
        filepath = os.path.join('./', filename) # root
        with open(filepath, 'rb') as f:
            return execute_sql(f)

    return load_data_from_sql

# split content and execute line by line
def execute_sql(f):
    with connection.cursor() as cursor:
        file_data = f.readlines()
        statement = ''
        delimiter = ';\n'
        for line in file_data:
            line = line.decode("utf-8")
            statement += line 
            if line.endswith(delimiter):
                if delimiter != ';\n':
                    statement = statement.replace(';', '; --').replace(delimiter, ';')
                cursor.execute(statement) # execute current statement
                statement = '' # begin collect next statement