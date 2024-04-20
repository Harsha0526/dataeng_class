import json
from google.cloud import pubsub_v1

def publish_messages(project_id, topic_id, filename):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    
    with open(filename, 'r') as file:
        records = json.load(file)

    for record in records:
        message_bytes = json.dumps(record).encode('utf-8')
        future = publisher.publish(topic_path, message_bytes)
        print(future.result())  

    print(f"Published messages to {topic_path}.")

if __name__ == "__main__":
    PROJECT_ID = "dataengineering-420503"
    TOPIC_ID = "my-topic"
    FILENAME = 'bcsample.json'
    
    publish_messages(PROJECT_ID, TOPIC_ID, FILENAME)