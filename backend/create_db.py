import cx_Oracle
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME")

# Ensure environment variables are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SERVICE_NAME]):
    raise ValueError("Missing one or more required environment variables for DB connection.")

# Connect to Oracle Database using cx_Oracle
dsn_tns = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE_NAME)
connection = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn_tns)
cursor = connection.cursor()

# Drop existing tables
drop_table_queries = [
    "DROP TABLE financials CASCADE CONSTRAINTS",
    "DROP TABLE assets CASCADE CONSTRAINTS",
    "DROP TABLE assets_maintenance CASCADE CONSTRAINTS",
    "DROP TABLE cradles CASCADE CONSTRAINTS",
    "DROP TABLE vessels CASCADE CONSTRAINTS",
    "DROP TABLE inventory CASCADE CONSTRAINTS",
    "DROP TABLE trolleys CASCADE CONSTRAINTS",
    "DROP TABLE lifts CASCADE CONSTRAINTS",
    "DROP TABLE work_orders CASCADE CONSTRAINTS",
    "DROP TABLE wheels_load CASCADE CONSTRAINTS",
    "DROP TABLE rails CASCADE CONSTRAINTS",
    "DROP TABLE wheels_temperature CASCADE CONSTRAINTS",
]

for query in drop_table_queries:
    try:
        cursor.execute(query)
        print(f"Table dropped successfully: {query.split()[2]}")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        if error.code != 942:  # Ignore table not found error
            print(f"Error dropping table: {query.split()[2]} - {error.message}")

create_table_queries = [

    """
    CREATE TABLE assets (
        id VARCHAR2(100) PRIMARY KEY,
        assetType VARCHAR2(100),
        name VARCHAR2(100),
        description VARCHAR2(255),
        status VARCHAR2(50),
        createdAt TIMESTAMP,
        updatedAt TIMESTAMP
    )
    """,
"""
CREATE TABLE financials (
    id VARCHAR2(100) PRIMARY KEY,
    recordDate DATE NOT NULL,
    dockingFees NUMBER DEFAULT 0 NOT NULL,              
    onDockingFees NUMBER DEFAULT 0 NOT NULL,            
    undockingFees NUMBER DEFAULT 0 NOT NULL,            
    maintenanceFees NUMBER DEFAULT 0 NOT NULL,          
    otherServiceFees NUMBER DEFAULT 0 NOT NULL,        

    totalRevenue NUMBER DEFAULT 0 NOT NULL,  

    laborCosts NUMBER DEFAULT 0 NOT NULL,              
    dockOperationCosts NUMBER DEFAULT 0 NOT NULL,       
    equipmentCosts NUMBER DEFAULT 0 NOT NULL,          
    administrativeCosts NUMBER DEFAULT 0 NOT NULL,   

    totalExpenses NUMBER DEFAULT 0 NOT NULL,  
    netProfitLoss NUMBER DEFAULT 0 NOT NULL,   

    assetId VARCHAR2(100),
    CONSTRAINT fkFinancialsAssetId FOREIGN KEY (assetId) REFERENCES assets(id)
)
"""
,
    """
    CREATE TABLE cradles (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        cradleName VARCHAR2(100),
        capacity NUMBER,
        maxShipLength NUMBER,
        status VARCHAR2(50),
        location VARCHAR2(100),
        lastMaintenanceDate TIMESTAMP,
        nextMaintenanceDue TIMESTAMP,
        operationalSince TIMESTAMP,
        notes VARCHAR2(255),
        occupancy VARCHAR2(100),
        currentLoad NUMBER,
        structuralStress VARCHAR2(50),
        wearLevel VARCHAR2(50),
        assetId VARCHAR2(100),
        CONSTRAINT fkCradleAssetId FOREIGN KEY (assetId) REFERENCES assets(id)
    )
    """,
    """
    CREATE TABLE vessels (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        vesselName VARCHAR2(100) UNIQUE,
        vesselType VARCHAR2(50),
        weight NUMBER,
        length NUMBER,
        width NUMBER,
        draft NUMBER,
        status VARCHAR2(50),
        lastMaintenanceDate TIMESTAMP,
        nextMaintenanceDue TIMESTAMP,
        birthingArea VARCHAR2(100),
        operationalSince TIMESTAMP,
        ownerCompany VARCHAR2(100),
        notes VARCHAR2(255),
        assignedCradle VARCHAR2(100),
        transferCompleted VARCHAR2(50),
        estimatedTimeToDestination VARCHAR2(50),
        bearingTemperature NUMBER,
        assetId VARCHAR2(100),
        CONSTRAINT fkVesselAssetId FOREIGN KEY (assetId) REFERENCES assets(id),
        CONSTRAINT fkVesselAssignedCradle FOREIGN KEY (assignedCradle) REFERENCES cradles(id)
    )
    """,
    """
    CREATE TABLE inventory (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        lastUpdated TIMESTAMP,
        name VARCHAR2(100),
        location VARCHAR2(100),
        quantity NUMBER,
        assetId VARCHAR2(100),
        CONSTRAINT fkInventoryAssetId FOREIGN KEY (assetId) REFERENCES assets(id)
    )
    """,
    """
    CREATE TABLE rails (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        railName VARCHAR2(100),
        length NUMBER,
        capacity NUMBER,
        status VARCHAR2(50),
        lastInspectionDate TIMESTAMP,
        nextInspectionDue TIMESTAMP,
        operationalSince TIMESTAMP,
        notes VARCHAR2(255),
        assetId VARCHAR2(100),
        CONSTRAINT fkRailAssetId FOREIGN KEY (assetId) REFERENCES assets(id)
    )
    """,
    """
    CREATE TABLE trolleys (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        trolleyName VARCHAR2(100),
        wheelCount NUMBER,
        railId VARCHAR2(100),
        assignedVesselId VARCHAR2(100),
        status VARCHAR2(50),
        lastMaintenanceDate TIMESTAMP,
        nextMaintenanceDue TIMESTAMP,
        notes VARCHAR2(255),
        maxCapacity NUMBER,
        currentLoad NUMBER,
        speed NUMBER,
        location VARCHAR2(255),
        utilizationRate VARCHAR2(50),
        averageTransferTime VARCHAR2(50),
        assetId VARCHAR2(100),
        CONSTRAINT fkTrolleyAssetId FOREIGN KEY (assetId) REFERENCES assets(id),
        CONSTRAINT fkTrolleyRailId FOREIGN KEY (railId) REFERENCES rails(id),
        CONSTRAINT fkTrolleyAssignedVesselId FOREIGN KEY (assignedVesselId) REFERENCES vessels(id)
    )
    """,
    """
    CREATE TABLE lifts (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        liftName VARCHAR2(100),
        platformLength NUMBER,
        platformWidth NUMBER,
        maxShipDraft NUMBER,
        location VARCHAR2(255),
        status VARCHAR2(50),
        lastMaintenanceDate TIMESTAMP,
        nextMaintenanceDue TIMESTAMP,
        operationalSince TIMESTAMP,
        assignedVesselId VARCHAR2(100),
        notes VARCHAR2(255),
        currentLoad NUMBER,
        historicalUsageHours NUMBER,
        maxCapacity NUMBER,
        utilizationRate VARCHAR2(50),
        averageTransferTime VARCHAR2(50),
        assetId VARCHAR2(100),
        CONSTRAINT fkLiftAssetId FOREIGN KEY (assetId) REFERENCES assets(id),
        CONSTRAINT fkLiftAssignedVesselId FOREIGN KEY (assignedVesselId) REFERENCES vessels(id)
    )
    """,
    """
    CREATE TABLE assets_maintenance (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        assetId VARCHAR2(100),
        description VARCHAR2(255),
        datePerformed TIMESTAMP,
        performedBy VARCHAR2(255),
        nextDueDate TIMESTAMP,
        assetName VARCHAR2(100),
        historicalUsageHours NUMBER,
        remainingLifespanHours NUMBER,
        statusSummary VARCHAR2(255),
        shipsInTransfer NUMBER,
        operationalLifts NUMBER,
        operationalTrolleys NUMBER,
        CONSTRAINT fkMmaintenanceAssetId FOREIGN KEY (assetId) REFERENCES assets(id)
    )
    """,
    """
    CREATE TABLE work_orders (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        workType VARCHAR2(50),
        assignedTo VARCHAR2(100),
        startDate TIMESTAMP,
        endDate TIMESTAMP,
        status VARCHAR2(50),
        notes VARCHAR2(255),
        vesselName VARCHAR2(100),
        vesselId VARCHAR2(100), 
        CONSTRAINT fkWorkOrderVesselId FOREIGN KEY (vesselId) REFERENCES vessels(id)   
    )
    """,
    """
    CREATE TABLE wheels_load (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        trolley VARCHAR2(100),
        wheel VARCHAR2(100),
        currentLoad NUMBER,
        CONSTRAINT fkWheelsLoadTrolleyId FOREIGN KEY (trolley) REFERENCES trolleys(id)
    )
    """,
    """
    CREATE TABLE wheels_temperature (
        id VARCHAR2(100) PRIMARY KEY,
        updatedAt TIMESTAMP,
        trolley VARCHAR2(100),
        wheel VARCHAR2(100),
        bearingTemperature NUMBER,
        CONSTRAINT fkWheelsTempTrolley_id FOREIGN KEY (trolley) REFERENCES trolleys(id)
    )
    """
]

# Execute table creation queries
for query in create_table_queries:
    try:
        cursor.execute(query)
        print(f"Table created successfully: {query.split()[2]}")
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f"Error creating table: {query.split()[2]} - {error.message}")

# Close connection
cursor.close()
connection.close()
