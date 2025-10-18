# NYC 311 Service Requests Web App

## Overview
This project provides a small web application to explore NYC 311 Service Requests.  
It includes an **ETL pipeline**, a **MySQL database**, a **Flask web app**, **automated tests**, and **Docker Compose** for easy setup.

---

## Dataset
- Source: NYC 311 Service Requests (subset used for this project).  
- CSV Slice Used: `data/311_Service_Requests_from_2010_to_Present_20251016.csv` (Insert  1500 rows inside mysql).  I used this for run of elt.py file.

- CSV Slice Used: `data/fixture.csv` (first 50 rows for testing).  I used this for testing of CI-CD.
- Columns:  
  `Unique Key`, `Created Date`, `Closed Date`, `Agency`, `Agency Name`, `Complaint Type`, `Descriptor`, `Borough`, `City`, `Latitude`, `Longitude`, `Status`, `Resolution Description`

---

## Project Structure
1. Need to clone repo; # git clone <repo-url>
2. Create a .env file with database credentials:
3. Build and Start Docker Compose # docker compose up --build
4. Run ETL # docker compose exec app python etl/etl.py
5. Access Web App # http://localhost:5000/
6. Run Tests # docker compose exec app pytest -q
7. CI/CD  #.github/workflows/ci.yml

