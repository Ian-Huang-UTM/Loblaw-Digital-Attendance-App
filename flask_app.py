import os
from google.cloud import bigquery
from flask import Flask, jsonify

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/craigreed/mysite/application_default_credentials.json'
client = bigquery.Client(project='ld-grocery-shopping')

app = Flask(__name__)


# Define the SQL query as a constant
SQL_QUERY = """
    SELECT p_memberid as walletid
FROM `ds-bi-analytics-prod.bi_reporting.pcx_hybris_loyaltymembership`
WHERE p_householdid = @p_householdid
ORDER BY createdTS DESC
LIMIT 1;
"""



# Initialize a set to store unique promo codes
promo_codes = set()


@app.route("/")
def home():
    return 'Hello'

@app.route('/api/v1/walletid/<p_householdid>', methods=['GET'])
def get_order(p_householdid):
    # Use query parameters for safe SQL query execution
    query_params = [bigquery.ScalarQueryParameter('p_householdid', 'STRING', p_householdid)]
    job_config = bigquery.QueryJobConfig(query_parameters=query_params)

    try:
        # Execute the query
        query_job = client.query(SQL_QUERY, job_config=job_config)
        row = next(query_job.result())
        if row:
            wallet = dict(row.items())
            return jsonify(wallet)
    except StopIteration:
        return jsonify({"message": "walletid not found"}), 404
    except Exception as e:
        return str(e), 500  # Handle other exceptions with an internal server error



