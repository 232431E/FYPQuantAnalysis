# backend/config.py

# This file defines the database connection URL.
# Ensure you replace the placeholders with your actual MySQL credentials.

DATABASE_URL = "mysql+mysqlconnector://root:mySQL2025%21@localhost/fypquantanalysisplatform"

# Explanation of the connection string:
# mysql+mysqlconnector: Specifies the SQLAlchemy dialect and driver (MySQL Connector/Python)
# root: Your MySQL username
# mySQL2025%21: Your MySQL password (note the %21 is the URL-encoded version of !)
# @localhost: The hostname of your MySQL server (localhost for local development)
# /fypquantanalysisplatform: The name of your MySQL database