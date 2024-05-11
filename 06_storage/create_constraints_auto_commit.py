import time
import psycopg2
import argparse
import csv
import sys
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
DBname = "postgres"
DBuser = "postgres"
DBpwd = "Bhanu@162019"
TableName = 'CensusData'

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0
        row['County'] = row['County'].replace('\'', '')
    return ", ".join([f"'{row[key]}'" if isinstance(row[key], str) else str(row[key]) for key in row])

def initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    parser.add_argument("-c", "--createtable", action="store_true")
    args = parser.parse_args()
    return args.datafile, args.createtable

def readdata(fname):
    logger.info(f"Reading data from file: {fname}")
    try:
        with open(fname, mode="r") as fil:
            dr = csv.DictReader(fil)
            rowlist = [row for row in dr]
        return rowlist
    except FileNotFoundError:
        logger.error(f"File '{fname}' not found.")
        sys.exit(1)

def dbconnect():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database=DBname,
            user=DBuser,
            password=DBpwd,
        )
        connection.autocommit = True
        logger.info("Connected to the database.")
        return connection
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to the database: {e}")
        sys.exit(1)

def create_table(conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TableName} (
                    CensusTract         NUMERIC PRIMARY KEY,
                    State               TEXT,
                    County              TEXT,
                    TotalPop            INTEGER,
                    Men                 INTEGER,
                    Women               INTEGER,
                    Hispanic            DECIMAL,
                    White               DECIMAL,
                    Black               DECIMAL,
                    Native              DECIMAL,
                    Asian               DECIMAL,
                    Pacific             DECIMAL,
                    Citizen             DECIMAL,
                    Income              DECIMAL,
                    IncomeErr           DECIMAL,
                    IncomePerCap        DECIMAL,
                    IncomePerCapErr     DECIMAL,
                    Poverty             DECIMAL,
                    ChildPoverty        DECIMAL,
                    Professional        DECIMAL,
                    Service             DECIMAL,
                    Office              DECIMAL,
                    Construction        DECIMAL,
                    Production          DECIMAL,
                    Drive               DECIMAL,
                    Carpool             DECIMAL,
                    Transit             DECIMAL,
                    Walk                DECIMAL,
                    OtherTransp         DECIMAL,
                    WorkAtHome          DECIMAL,
                    MeanCommute         DECIMAL,
                    Employed            INTEGER,
                    PrivateWork         DECIMAL,
                    PublicWork          DECIMAL,
                    SelfEmployed        DECIMAL,
                    FamilyWork          DECIMAL,
                    Unemployment        DECIMAL
                );
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{TableName}_State ON {TableName}(State);")
            logger.info(f"Table '{TableName}' created.")
        except psycopg2.Error as e:
            logger.error(f"Failed to create table: {e}")
            sys.exit(1)

def load(conn, cmd_list):
    with conn.cursor() as cursor:
        logger.info(f"Loading {len(cmd_list)} rows")
        start = time.perf_counter()
        for cmd in cmd_list:
            try:
                cursor.execute(cmd)
            except psycopg2.errors.UniqueViolation:
                logger.warning("Skipping duplicate record.")
        elapsed = time.perf_counter() - start
        logger.info(f'Finished loading. Elapsed time: {elapsed:0.4f} seconds')

        cursor.execute(f"SELECT EXISTS (SELECT * FROM information_schema.table_constraints WHERE table_name = '{TableName}' AND constraint_type = 'PRIMARY KEY');")
        primary_key_exists = cursor.fetchone()[0]

        if not primary_key_exists:
            try:
                cursor.execute(f"ALTER TABLE {TableName} ADD PRIMARY KEY (CensusTract);")
                logger.info(f"Added primary key for {TableName}")
            except psycopg2.Error as e:
                logger.error(f"Failed to add primary key: {e}")

def main():
    datafile, create_table = initialize()
    conn = dbconnect()
    row_list = readdata(datafile)
    cmd_list = [f"INSERT INTO {TableName} VALUES ({row2vals(row)});" for row in row_list]

    if create_table:
        create_table(conn)
    else:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{TableName}');")
            table_exists = cursor.fetchone()[0]

        if not table_exists:
            create_table(conn)

    load(conn, cmd_list)

if __name__ == "__main__":
    main()
