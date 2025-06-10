from utils.sql import SafeSQL
from utils.logging import path_log, debug, gotenv


class DataClient:

    @debug
    def __init__(self):

        try:

            # Get the sql config from the environment variables
            sql_config = {
                'user': gotenv('MYSQL_USER'),
                'password': gotenv('MYSQL_PASSWORD'),
                'host': gotenv('MYSQL_HOST'),
                'database': gotenv('MYSQL_DATABASE')
            }

            # Establish a SafeSQL connection
            self.sql = SafeSQL(**sql_config, verbose=True)

            print("MySQL Connection Successful.")

            self.sql.run('SELECT * FROM user_info limit 1;')
            self.columns = self.sql.cursor.column_names

        except Exception as err:
            path_log('MySQL Connection Failed', err)

    @debug
    def handle_submit(self, user_info: dict):
        """
        Handles a submission by inserting user info into the database
        """
        print(f"User Info: {user_info}")
        values = tuple([user_info[col] for col in self.columns])
        print(values)

        self.sql.run_file('sql/append.sql', params=values)

        self.sql.commit()
