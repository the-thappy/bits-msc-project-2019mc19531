import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from datetime import timedelta, datetime
from apache_beam.io.gcp.internal.clients import bigquery


GOOGLE_CLOUD_PROJECT = "thappy"
PUBSUB_SUBSCRIPTION = f"projects/{GOOGLE_CLOUD_PROJECT}/subscriptions/data-sub"
BIGQUERY_TABLE = "thappy.bits_data"
BIGQUERY_TABLE = bigquery.TableReference(projectId="thappy", datasetId="thappy", tableId="bits_data")
BIGQUERY_SCHEMA = "PRICE:FLOAT64,TICKER:STRING,CURRENT_TS:DATETIME,INDICATOR:STRING"
window_size = timedelta(minutes=1).total_seconds()  # in seconds


def add_key_func(element):
    import json
    element = json.loads(element.decode("utf-8"))
    return (element["TICKER"], element)


class ParseInputData(beam.DoFn):
    """Custom ParallelDo class to apply a custom transformation"""

    def process(self, element, timestamp=beam.DoFn.TimestampParam, window=beam.DoFn.WindowParam):
        # example window - ('ALPHABET_INC', [{'TIME': '2022-04-21 13:30:28.024924', 'TICKER': 'ALPHABET_INC', 'PRICE': 10.0}, {'TIME': '2022-04-21 13:30:29.028450', 'TICKER': 'ALPHABET_INC', 'PRICE': 10.4}, {'TIME': '2022-04-21 13:30:30.033912', 'TICKER': 'ALPHABET_INC', 'PRICE': 10.8}, {'TIME': '2022-04-21 13:30:31.036173', 'TICKER': 'ALPHABET_INC', 'PRICE': 11.2}])
        from datetime import datetime
        new_element = {"PRICE": 0, "TICKER": element[0], "CURRENT_TS": datetime.now(), "INDICATOR": "BUY"}
        yield new_element


def run():
    pipeline_options = PipelineOptions()
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.gcp.pubsub.ReadFromPubSub(subscription=PUBSUB_SUBSCRIPTION)
            | "Fixed Window" >> beam.WindowInto(beam.window.FixedWindows(window_size))
            | "Add Key" >> beam.Map(add_key_func)
            | "Group By Key" >> beam.GroupByKey()
            | "CustomParse" >> beam.ParDo(ParseInputData())
            | "WriteToBigQuery"
            >> beam.io.WriteToBigQuery(
                BIGQUERY_TABLE,
                schema=BIGQUERY_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            )
        )


if __name__ == "__main__":
    run()
