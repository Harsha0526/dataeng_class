import time
import psycopg2
import argparse
import csv

DBname = "postgres"
DBuser = "postgres"
DBpwd = "Bhanu@162019"
TableName = 'CensusData_Table'

def row2vals(row):
    # Handle null values by replacing them with 0
    for key in row:
        if not row[key]:
            row[key] = 0
        # Eliminate quotes within literals to prevent SQL injection
        row[key] = str(row[key]).replace("'", "''")
        
    # Construct the SQL values string
    ret = f"""
           {row['CensusTract']},            -- CensusTract
           '{row['State']}',                -- State
           '{row['County']}',               -- County
           {row['TotalPop']},               -- TotalPop
           {row['Men']},                    -- Men
           {row['Women']},                  -- Women
           {row['Hispanic']},               -- Hispanic
           {row['White']},                  -- White
           {row['Black']},                  -- Black
           {row['Native']},                 -- Native
           {row['Asian']},                  -- Asian
           {row['Pacific']},                -- Pacific
           {row['Citizen']},                -- Citizen
           {row['Income']},                 -- Income
           {row['IncomeErr']},              -- IncomeErr
           {row['IncomePerCap']},           -- IncomePerCap
           {row['IncomePerCapErr']},        -- IncomePerCapErr
           {row['Poverty']},                -- Poverty
           {row['ChildPoverty']},           -- ChildPoverty
           {row['Professional']},           -- Professional
           {row['Service']},                -- Service
           {row['Office']},                 -- Office
           {row['Construction']},           -- Construction
           {row['Production']},             -- Production
           {row['Drive']},                  -- Drive
           {row['Carpool']},                -- Carpool
           {row['Transit']},                -- Transit
           {row['Walk']},                   -- Walk
           {row['OtherTransp']},            -- OtherTransp
           {row['WorkAtHome']},             -- WorkAtHome
           {row['MeanCommute']},            -- MeanCommute
           {row['Employed']},               -- Employed
           {row['PrivateWork']},            -- PrivateWork
           {row['PublicWork']},             -- PublicWork
           {row['SelfEmployed']},           -- SelfEmployed
           {row['FamilyWork']},             -- FamilyWork
           {row['Unemployment']}            -- Unemployment
        """

    return ret


def initialize():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datafile", required=True)
    parser.add_argument("-c", "--createtable", action="store_true")
    args = parser.parse_args()

    return args.datafile, args.createtable

# Read the input data file into a list of dictionaries
def readdata(fname):
    print(f"Reading from File: {fname}")
    with open(fname, mode="r") as fil:
        dr = csv.DictReader(fil)
        rowlist = list(dr)
    return rowlist

# Create the target table 
def createTable(conn):
    with conn.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TableName} (
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
            )
        """)
        print(f"Created {TableName} table")

# Load data into the database
def load(conn, icmdlist):
    with conn.cursor() as cursor:
        print(f"Loading {len(icmdlist)} rows")
        start = time.perf_counter()
        for cmd in icmdlist:
            try:
                cursor.execute(cmd)
            except psycopg2.errors.UniqueViolation:
                print("Skipping row due to duplicate primary key value")
                conn.rollback()  # Rollback the transaction to continue with the next row

        elapsed = time.perf_counter() - start
        print(f'Finished Loading. Elapsed Time: {elapsed:0.4} seconds')

def main():
    datafile, create_table = initialize()
    conn = psycopg2.connect(
        host="localhost",
        database=DBname,
        user=DBuser,
        password=DBpwd,
    )
    conn.autocommit = True

    row_list = readdata(datafile)
    cmd_list = [f"INSERT INTO {TableName} VALUES ({row2vals(row)});" for row in row_list]

    if create_table:
        createTable(conn)

    load(conn, cmd_list)

if __name__ == "__main__":
    main()
