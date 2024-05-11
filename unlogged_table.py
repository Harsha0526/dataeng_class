import time
import psycopg2
import argparse
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "Bhanu@162019"
StagingTableName = 'censusdata_staging'
MainTableName = 'CensusData'
Datafile = "filedoesnotexist"  # name of the data file to be loaded
CreateDB = False  # indicates whether the DB table should be (re)-created

def row2vals(row):
    for key in row:
        if not row[key]:
            row[key] = 0  # Handle null values
        row['County'] = row['County'].replace('\'', '')  # Remove quotes within literals

    return ", ".join([f"'{val}'" if isinstance(val, str) else str(val) for val in row.values()])

def initialize():
    global Datafile, CreateDB
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    parser.add_argument("-c", "--createtable", action="store_true")
    args = parser.parse_args()
    Datafile = args.datafile
    CreateDB = args.createtable

def readdata(fname):
    print(f"Reading data from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)
        return list(dr)

def getSQLcmnds(rowlist, table):
    cmdlist = []
    for row in rowlist:
        valstr = row2vals(row)
        cmdlist.append(valstr)
    return cmdlist

def dbconnect():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database=DBname,
            user=DBuser,
            password=DBpwd,
        )
        connection.autocommit = False
        return connection
    except psycopg2.Error as e:
        print(f"Failed to connect to the database: {e}")
        sys.exit(1)

def createStagingTable(conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f"""
                CREATE UNLOGGED TABLE IF NOT EXISTS {StagingTableName} (
                    CensusTract         NUMERIC,
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
            print(f"Created {StagingTableName} table")
        except psycopg2.Error as e:
            print(f"Failed to create staging table: {e}")
            sys.exit(1)

def loadStagingTable(conn, icmdlist):
    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows into \"{StagingTableName}\"")
        start = time.perf_counter()
        for cmd in icmdlist:
            try:
                cursor.execute(f"INSERT INTO {StagingTableName} VALUES ({cmd})")
            except psycopg2.Error as e:
                print(f"Failed to load data into staging table: {e}")
                conn.rollback()
                sys.exit(1)
        elapsed = time.perf_counter() - start
        print(f'Finished loading into \"{StagingTableName}\". Elapsed Time: {elapsed:0.4} seconds')

def appendDataToMainTable(conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f"INSERT INTO {MainTableName} SELECT * FROM {StagingTableName}")
            conn.commit()
            print(f"Appended data from {StagingTableName} to {MainTableName}")
        except psycopg2.Error as e:
            print(f"Failed to append data to main table: {e}")
            conn.rollback()
            sys.exit(1)

def createIndexAndConstraint(conn):
    with conn.cursor() as cursor:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{MainTableName}_State ON {MainTableName}(State);")
            cursor.execute(f"ALTER TABLE {MainTableName} ADD PRIMARY KEY (CensusTract);")
            print(f"Created index and constraint on {MainTableName}")
        except psycopg2.Error as e:
            print(f"Failed to create index and constraint: {e}")
            conn.rollback()
            sys.exit(1)

def main():
    initialize()
    conn = dbconnect()
    row_list = readdata(Datafile)
    staging_cmd_list = getSQLcmnds(row_list, StagingTableName)

    if CreateDB:
        createStagingTable(conn)

    loadStagingTable(conn, staging_cmd_list)
    appendDataToMainTable(conn)
    createIndexAndConstraint(conn)

if __name__ == "__main__":
    main()
