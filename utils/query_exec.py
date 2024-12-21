import re
import sqlite3
import yaml

def extract_sql_query(response):
    """Extract the SQL query from the response."""
    # Use regular expression to find the SQL query in the response
    query_match = re.search(r'```sql(.*?)```', response, re.DOTALL)
    if query_match:
        sql_query = query_match.group(1).strip()
        return sql_query
    else:
        return None

def execute_sql_query(sql_query):
    """Execute the provided SQL query and return the result."""
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    db_path = config['db_path']
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(sql_query)
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]

    connection.close()
    return result

def format_sql_result_to_table(data):
    """Format the SQL query result as a readable table."""
    if not data:
        return "No data found."

    headers = data[0].keys()
    rows = [list(item.values()) for item in data]
    table = f"{' | '.join(headers)}\n"
    table += '-' * len(table) + '\n'
    for row in rows:
        table += ' | '.join(map(str, row)) + '\n'
    return table