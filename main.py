import json
import os
import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

GOOGLE_CLOUD_PROJECT = "thappy"
PUBSUB_SUBSCRIPTION = f"projects/{GOOGLE_CLOUD_PROJECT}/subscriptions/data-sub"
BIGQUERY_TABLE = "test_table"
BIGQUERY_SCHEMA = "key:STRING,value:STRING"


class ParseInputData(beam.DoFn):
    """ Custom ParallelDo class to apply a custom transformation """

    def process(self, element: bytes, timestamp=beam.DoFn.TimestampParam, window=beam.DoFn.WindowParam):
        """
        Simple processing function to parse the data and add a timestamp
        For additional params see:
        https://beam.apache.org/releases/pydoc/2.7.0/apache_beam.transforms.core.html#apache_beam.transforms.core.DoFn
        """
        parsed = json.loads(element.decode("utf-8"))
        parsed["timestamp"] = timestamp.to_rfc3339()
        yield parsed


def run():
    pipeline_options = PipelineOptions()
    pipeline_options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ReadFromPubSub" >> beam.io.gcp.pubsub.ReadFromPubSub(
                subscription=PUBSUB_SUBSCRIPTION
            )
            | "CustomParse" >> beam.ParDo(ParseInputData())
            | "WriteToBigQuery" >> beam.io.WriteToBigQuery(
                BIGQUERY_TABLE,
                schema=BIGQUERY_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            )
        )


if __name__ == "__main__":
    run()