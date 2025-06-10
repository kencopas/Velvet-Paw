from collections.abc import Iterable
import csv

import mysql.connector
from mysql.connector import Error
from mysql.connector.types import RowType

from utils.logging import path_log


# Safe connection and cursor querying
class SafeSQL:

    """
    This class just simplifies MySQL operations with error handling
    and configuration.

    kwargs:
    - user: MySQL username
    - password: MySQL password
    - host: ip hostname
    - database: database name (optional)
    """

    def __init__(self, **kwargs) -> None:

        self.verbose = kwargs.pop('verbose', False)

        # Attempt to connect to mysql local instance
        try:
            self.connector = mysql.connector.connect(**kwargs)
        except Error as err:
            print("Could not connect to server:", err)
            raise err
            exit()

        # Initialize cursor
        self.cursor = self.connector.cursor()

        # Tracks error count and query count
        self.error_count = 0
        self.query_count = 0

    @staticmethod
    def prompt(text: str, options: tuple[str]) -> str:

        ans = input(f"{text} {options}")

        while ans not in options:
            ans = input(f"Please choose a valid option: {options}")

        return ans

    @staticmethod
    def unpacked(data: Iterable, *, remove_empty: bool = False) -> Iterable:

        # Remove empty iterables if specified
        if remove_empty:
            data = list(filter(bool, data))

        # While unpackable, unpack
        while (
            len(data) == 1
            and isinstance(data[0], Iterable)
            and not isinstance(data[0], (str, bytes))
        ):
            data = data[0]
            if remove_empty:
                data = list(filter(bool, data))

        # Return unpacked data
        return data

    # Executes a file given a filepath
    def run_file(self, fp: str, *, params: tuple = None, inserts: tuple = None):
        with open(fp, 'r') as f:
            script = f.read()
        if inserts:
            script = script.format(*inserts)
        if params:
            return self.cursor.execute(script, params)
        else:
            return self.run(script)

    # Writes a MySQL table to a csv file
    def to_csv(self, table: str, filepath: str) -> None:

        stuff = self.run(f"SELECT * FROM {table};")

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(stuff.pop(0))
            writer.writerows(stuff)

        path_log(f"{table} table data written to {filepath}")

    def run(self, sqlin: str) -> list[RowType] | list[list[RowType]]:

        """
        Safe query function, takes an sql script as text or a filepath,
        executes the contents, and returns a list of the results.
        """

        try:

            # Initialize list of outputs
            outputs = []
            rowcount = 0

            # Detect with argument is a filepath or sql query
            if len(sqlin) > 4 and sqlin[-4:] == ".sql":
                # Read file contents
                with open(sqlin, 'r') as f:
                    content = f.read()
            else:
                content = sqlin

            # Split potential multiquery into single queries by semicolon
            query_arr = [q.strip() for q in content.split(';') if q.strip()]

            # Run each query and append the result to the outputs
            for query in query_arr:

                # Execute query and increment query and row count
                self.cursor.execute(query)
                self.query_count += 1
                rowcount += self.cursor.rowcount

                # Fetch all the returned rows
                output = self.cursor.fetchall()

                # Retrieve the column names and insert them into the output
                if self.cursor.description and output:
                    col_names = [desc[0] for desc in self.cursor.description]
                    output.insert(0, col_names)

                # Append the query results to outputs
                outputs.append(output)

            self.verbose and print(
                f"Executed {len(query_arr)} queries."
                f"\n{rowcount} rows affected."
            )

            # unpacked the outputs list before returning
            outputs = self.unpacked(outputs)

            return outputs

        except Error as err:

            print(f"Failed to execute: '{sqlin}'\nError: {err}")
            self.error_count += 1

            return None

    # Safe commit function
    def commit(self) -> None:

        # If there are one or more errors, print
        if self.error_count > 0:
            print(f"{self.error_count} errors occured during query.")

        self.connector.commit()
        print(self.query_count, "queries committed.")

        # Reset error and query counters
        self.error_count, self.query_count = 0, 0

    def parse_file(
        self,
        fp: str,
        *,
        flag: str,
        params: tuple
    ):

        """
        The parse_file method takes a filepath, flag, and parameters. The file
        is read and separated into query sections by the delimiter '%%'. The
        parameters are then inserted into the query section with the specified
        flag between delimiters before that section is executed.
        """

        try:

            # Read the file contents
            with open(fp, 'r') as f:
                contents = f.read()

            # Split the file contents by the delimiter
            scripts = contents.split(r'%%')
            index = scripts.index(flag)

            # Get the target script and split by parameter flag
            script = scripts[index+1].split(r'{}')

            # Join the script back together inserting the parameters
            full_script = ''.join([
                line+str(param)
                for line, param in zip(script, params+('',))
            ])

            # Run the script and return the results
            return self.run(full_script)

        except Exception as e:
            print(f"Error parsing sql script:\n{e}")

    # Close the cursor and connection
    def close(self) -> None:

        print("Closing connection...")

        self.cursor.close()
        self.connector.close()
