import json
import subprocess
from google.cloud import bigquery


with open('schema.json',) as f:
    schema = json.load(f)

with open('config.json',) as f:
    config = json.load(f)

subprocess.call("gsutil -m cp * " + config['bucket'], shell=True)

#subprocess.call("gsutil ls " + config['bucket'], shell=True)

# Construct a BigQuery client object.
client = bigquery.Client()
table_id = config['plebiscito_table']

job_config = bigquery.LoadJobConfig(
    schema=schema,
    skip_leading_rows=1,
    # The source format defaults to CSV, so the line below is optional.
    source_format=bigquery.SourceFormat.CSV,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)
uri = config['bucket'] + "/*.csv.gz"

load_job = client.load_table_from_uri(
    uri, table_id, job_config=job_config
)  # Make an API request.

load_job.result()  # Waits for the job to complete.

destination_table = client.get_table(table_id)  # Make an API request.
print("Loaded {} rows.".format(destination_table.num_rows))


# query_job = client.query(
#     """
#     SELECT
#       CONCAT(
#         'https://stackoverflow.com/questions/',
#         CAST(id as STRING)) as url,
#       view_count
#     FROM `bigquery-public-data.stackoverflow.posts_questions`
#     WHERE tags like '%google-bigquery%'
#     ORDER BY view_count DESC
#     LIMIT 10"""
# )

# results = query_job.result()  # Waits for job to complete.

# for row in results:
#     print("{} : {} views".format(row.url, row.view_count))


print('holi')