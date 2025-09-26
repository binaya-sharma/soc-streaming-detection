import sys, six
# temporary fix for kafka.vendor.six import issues
sys.modules['kafka.vendor.six'] = six
sys.modules['kafka.vendor.six.moves'] = six.moves

import os, json, time, uuid, random, argparse, datetime
from kafka import KafkaProducer

def now_utc():
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

def make_event(result="SUCCESS", src_ip=None, username=None, dst_port=22):
    return {
        "event_time": now_utc(),
        "provider": "internal_sim",
        "sub": f"sim|{uuid.uuid4().hex[:8]}",
        "email": username or f"user{random.randint(1,999)}@example.com",
        "email_verified": result == "SUCCESS",
        "username": username or f"user{random.randint(1,999)}",
        "result": result,# "SUCCESS" or "FAILURE"
        "src_ip": src_ip or f"192.168.1.{random.randint(2,254)}",
        "dst_ip": "10.0.0.5",
        "dst_port": dst_port,
        "auth_method": "password",
        "hostname": os.environ.get("HOSTNAME", "python-ingest"),
        "user_agent": "sim-producer/1.0",
        "trace_id": uuid.uuid4().hex
    }

def main():
    ap = argparse.ArgumentParser() 
    ap.add_argument("--bootstrap", default=os.getenv("BOOTSTRAP", "kafka:9092")) # Kafka bootstrap server on env 
    ap.add_argument("--topic", default=os.getenv("TOPIC", "auth_events"))
    ap.add_argument("--rate", type=float, default=float(os.getenv("RATE", "5.0")), help="events per second (approx)")
    ap.add_argument("--mode", choices=["random","bruteforce","spray","success"], default=os.getenv("MODE","random"))
    ap.add_argument("--duration", type=int, default=int(os.getenv("DURATION","60")), help="seconds to run (0 = forever)")
    args = ap.parse_args()
# --bootstrap kafka:9092 --topic auth_events --rate 10 --mode random --duration 60

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        linger_ms=10
    )

    print(f"[producer] bootstrap={args.bootstrap} topic={args.topic} mode={args.mode} rate={args.rate}/s")

    start = time.time()
    sent = 0

    # Pre-config for patterns
    bf_ip = "203.0.113.8" # single IP failing many times (brute force)
    spray_pwd = "HelloNepal2024" # same password across many users (password spray)

    while True:
        if args.mode == "random":
            # random mix
            evt = make_event(result="FAILURE" if random.random()<0.5 else "SUCCESS")
        elif args.mode == "bruteforce":
            # many failures from same IP + occasional success
            evt = make_event(result="FAILURE" if random.random()<0.9 else "SUCCESS", src_ip=bf_ip, username="alice")
        elif args.mode == "spray":
            # same password attempted across users -> we encode password hint in user_agent
            user = f"user{random.randint(1,50)}@example.com"
            evt = make_event(result="FAILURE", username=user)
            evt["user_agent"] = f"sim-producer/1.0 pwd={spray_pwd}"
        else:  # success-only
            evt = make_event(result="SUCCESS")

        producer.send(args.topic, evt)
        sent += 1

        # pacing
        if args.rate > 0:
            time.sleep(1.0 / args.rate)

        if args.duration > 0 and (time.time() - start) >= args.duration:
            break

    producer.flush()
    print(f"[producer] done. sent={sent} duration={int(time.time()-start)}s")

if __name__ == "__main__":
    main()

'''
docker compose run --rm python-producer \
  python producer.py \
  --bootstrap kafka:9092 \
  --topic auth_events \
  --mode bruteforce \
  --rate 10 \
  --duration 20
'''