import sys, six
# temporary fix for kafka.vendor.six import issues
sys.modules['kafka.vendor.six'] = six
sys.modules['kafka.vendor.six.moves'] = six.moves

from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "auth_events",
    bootstrap_servers="kafka:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="test-consumer"
)

print("Listening on auth_events...")
for msg in consumer:
    print(msg.value.decode("utf-8"))

