from confluent_kafka import Consumer, KafkaException

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'consumer-group-1',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['invoice-events'])
print("Subscribing to:", consumer.list_topics().topics.keys())


try:
    while True:
        print("Waiting for messages...")
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("No message received")
            continue
        if msg.error():
            raise KafkaException(msg.error())
        print(f"Received: {msg.value().decode('utf-8')}")
finally:
    consumer.close()
