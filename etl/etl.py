import os, sys, time, json
import pandas as pd
import pymysql
from dotenv import load_dotenv
import psutil

# -------------------------------------------
# CONFIGURATION
# -------------------------------------------
USECOLS = [
    "Unique Key","Created Date","Closed Date","Agency","Agency Name",
    "Complaint Type","Descriptor","Borough","City",
    "Latitude","Longitude","Status","Resolution Description"
]

DTYPES = {
    "Unique Key": "Int64",
    "Agency": "string",
    "Agency Name": "string",
    "Complaint Type": "string",
    "Descriptor": "string",
    "Borough": "string",
    "City": "string",
    "Latitude": "float64",
    "Longitude": "float64",
    "Status": "string",
    "Resolution Description": "string",
}
DATE_COLS = ["Created Date","Closed Date"]

# -------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------
def _req(name):
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v

def connect():
    load_dotenv()
    return pymysql.connect(
        host=_req("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=_req("DB_USER"),
        password=_req("DB_PASSWORD"),
        database=_req("DB_NAME"),
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4"
    )

# -------------------------------------------
# ETL STEPS
# -------------------------------------------
def clean_chunk(df):
    df = df[USECOLS].copy()
    for c, t in DTYPES.items():
        if c in df:
            df[c] = df[c].astype(t)
    for c in DATE_COLS:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    df = df[(df["Created Date"].notna()) & (df["Created Date"] >= "2010-01-01")]
    df["Borough"] = df["Borough"].fillna("UNKNOWN").replace({"": "UNKNOWN", "Unspecified": "UNKNOWN"})
    df["Complaint Type"] = df["Complaint Type"].fillna("UNKNOWN")
    df["month_key"] = df["Created Date"].dt.strftime("%Y-%m")

    out = pd.DataFrame({
        "request_id": df["Unique Key"].astype("Int64"),
        "created_datetime": df["Created Date"],
        "closed_datetime": df["Closed Date"],
        "agency": df["Agency"],
        "agency_name": df["Agency Name"],
        "complaint_type": df["Complaint Type"],
        "descriptor": df["Descriptor"],
        "borough": df["Borough"],
        "city": df["City"],
        "latitude": df["Latitude"],
        "longitude": df["Longitude"],
        "status": df["Status"],
        "resolution_description": df["Resolution Description"],
        "month_key": df["month_key"]
    })
    out = out[out["request_id"].notna()]
    return out

def insert_batch(conn, rows):
    sql = """
    INSERT INTO service_requests
    (request_id, created_datetime, closed_datetime, agency, agency_name, complaint_type, descriptor,
     borough, city, latitude, longitude, status, resolution_description, month_key)
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
      created_datetime=VALUES(created_datetime),
      closed_datetime=VALUES(closed_datetime),
      agency=VALUES(agency),
      agency_name=VALUES(agency_name),
      complaint_type=VALUES(complaint_type),
      descriptor=VALUES(descriptor),
      borough=VALUES(borough),
      city=VALUES(city),
      latitude=VALUES(latitude),
      longitude=VALUES(longitude),
      status=VALUES(status),
      resolution_description=VALUES(resolution_description),
      month_key=VALUES(month_key)
    """
    with conn.cursor() as cur:
        cur.executemany(sql, rows)

# -------------------------------------------
# MAIN ETL FUNCTION
# -------------------------------------------
def run_etl():
    file_path = "data/311_Service_Requests_from_2010_to_Present_20251016.csv"  # ✅ update if your CSV name differs
    month_key = "2023-01"
    limit_rows = 1500 

    print(f"Loading {limit_rows} rows from {file_path} ...")

    conn = connect()
    total = 0
    t0 = time.time()

    try:
        chunks = pd.read_csv(
            file_path, usecols=USECOLS, dtype=DTYPES,
            parse_dates=DATE_COLS, chunksize=10000, low_memory=False
        )

        for chunk in chunks:
            df = clean_chunk(chunk)
            df = df.head(limit_rows - total)
            tuples = []

            for r in df.itertuples(index=False):
                created_dt = r.created_datetime.to_pydatetime() if pd.notna(r.created_datetime) else None
                closed_dt = r.closed_datetime.to_pydatetime() if pd.notna(r.closed_datetime) else None

                tuples.append((
                    int(r.request_id),
                    created_dt,
                    closed_dt,
                    (r.agency if pd.notna(r.agency) else None),
                    (r.agency_name if pd.notna(r.agency_name) else None),
                    (r.complaint_type if pd.notna(r.complaint_type) else "UNKNOWN"),
                    (r.descriptor if pd.notna(r.descriptor) else None),
                    (r.borough if pd.notna(r.borough) else "UNKNOWN"),
                    (r.city if pd.notna(r.city) else None),
                    (float(r.latitude) if not pd.isna(r.latitude) else None),
                    (float(r.longitude) if not pd.isna(r.longitude) else None),
                    (r.status if pd.notna(r.status) else None),
                    (r.resolution_description if pd.notna(r.resolution_description) else None),
                    r.month_key
                ))

            insert_batch(conn, tuples)
            conn.commit()
            total += len(tuples)
            print(f"Inserted no of {total} rows")

            if total >= limit_rows:
                break

        print(f"[Total rows inserted: {total} in {time.time() - t0:.2f}s")

    except Exception as e:
        print("❌ ETL FAILED:", e)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

# -------------------------------------------
if __name__ == "__main__":
    run_etl()
