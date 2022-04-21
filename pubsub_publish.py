from google.cloud import pubsub_v1
import datetime
import json
import time

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("thappy", "topic")
stocks = ["ALPHABET_INC", "BOEING_CORP", "CITADEL", "DELTA_AIR"]
message_count = 4
publish_futures = []
price = 10.0

for i in range(message_count):
	for stock in stocks:
		data = json.dumps({"TIME": datetime.datetime.now(), "TICKER": stock, "PRICE": price}, default=str).encode("utf-8")
		price = round(price + 0.10, 2)
		publish_future = publisher.publish(topic_path, data)
		publish_futures.append(publish_future)
	time.sleep(1)	

for future in publish_futures:
	print(future.result())
