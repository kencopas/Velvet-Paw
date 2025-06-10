from utils.sql import SafeSQL
from utils.logging import gotenv
from mysql.connector import Error
from dotenv import load_dotenv

"""

    Runs initialization script

"""

try:

    load_dotenv()

    table = gotenv('MYSQL_TABLE')

    # Get the sql config from the environment variables
    sql_config = {
        'user': gotenv('MYSQL_USER'),
        'password': gotenv('MYSQL_PASSWORD'),
        'host': gotenv('MYSQL_HOST')
    }

    # Establish a SafeSQL connection
    sql = SafeSQL(**sql_config)

    # Run the initialization script
    sql.run('sql/init.sql')

    # Retrieve the number of columns
    col_count = len(sql.cursor.column_names)

    # Format the script for append.sql
    append_script = f"""
        INSERT INTO
            {table}
        VALUES
            ({', '.join([r'%s' for _ in range(col_count)])});
    """

    # Write the script to a file
    with open('sql/append.sql', 'w') as f:
        f.write(append_script)

    # Commit and close connection
    sql.commit()
    sql.close()

except Error as err:
    print(f"{type(err).__name__}: {err}")
