import psycopg2
import argparse
from io import StringIO
import time

# Database connection parameters
DBname = "postgres"
DBuser = "postgres"
DBpwd = "Bhanu@162019"  # Replace 'your_password' with the actual password
TableName = 'censusdata_copy_from'

# SQL statement to create the table
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TableName} (
    CensusTract VARCHAR(255),
    State VARCHAR(255),
    County VARCHAR(255),
    TotalPop INT,
    Men INT,
    Women INT,
    Hispanic FLOAT,
    White FLOAT,
    Black FLOAT,
    Native FLOAT,
    Asian FLOAT,
    Pacific FLOAT,
    Citizen INT,
    Income FLOAT,
    IncomeErr FLOAT,
    IncomePerCap FLOAT,
    IncomePerCapErr FLOAT,
    Poverty FLOAT,
    ChildPoverty FLOAT,
    Professional FLOAT,
    Service FLOAT,
    Office FLOAT,
    Construction FLOAT,
    Production FLOAT,
    Drive FLOAT,
    Carpool FLOAT,
    Transit FLOAT,
    Walk FLOAT,
    OtherTransp FLOAT,
    WorkAtHome FLOAT,
    MeanCommute FLOAT,
    Employed INT,
    PrivateWork FLOAT,
    PublicWork FLOAT,
    SelfEmployed FLOAT,
    FamilyWork FLOAT,
    Unemployment FLOAT
);
"""

def create_table(cursor):
    try:
        # Execute the table creation SQL
        print("Table does not exist. Attempting to create it...")
        print("Executing table creation SQL...")
        cursor.execute(create_table_sql)
        print("Table created successfully.")
    except psycopg2.Error as e:
        print("Error creating table:", e)

def load_data(cursor, datafile):
    try:
        start_time = time.time()

        # Load data into the table using the copy_from function
        with open(datafile, 'r') as f:
            # Skip the header line
            next(f)
            for line in f:
                # Split the line by commas
                data = line.strip().split(',')
                # Replace non-numeric values with NULL
                data = ['\\N' if not x.strip() else x.strip() for x in data]
                # Join the modified data back into a CSV string
                modified_line = ','.join(data)
                print("Modified line:", modified_line)
                cursor.copy_from(StringIO(modified_line), TableName, sep=',')

        # Commit the transaction
        conn.commit()

        end_time = time.time()
        runtime = end_time - start_time
        print(f"Data loaded in {runtime:.2f} seconds.")
    except psycopg2.Error as e:
        print("Error loading data:", e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    args = parser.parse_args()

    Datafile = args.datafile

    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DBname,
            user=DBuser,
            password=DBpwd,
            host='localhost',  # Assuming the database is running locally
            port=5432
        )

        # Create a cursor object
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        create_table(cursor)

        # Load data into the table
        load_data(cursor, Datafile)

    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
