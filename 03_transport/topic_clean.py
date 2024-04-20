from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError

def clean_subscription_messages(project_id, subscription_id):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def message_callback(message):
        print(f"Message Received and discarded message: {message.data.decode('utf-8')}")
        message.ack()

    print(f"Listening for messages on {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=message_callback)

    with subscriber:
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            print("Subscription canceled by user.")
        except TimeoutError:
            print("Timed out waiting for messages.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            streaming_pull_future.cancel()

    print("Finished listening for messages.")

if __name__ == "__main__":
    PROJECT_ID = "dataengineering-420503"
    SUBSCRIPTION_ID = "my-sub"
    
    clean_subscription_messages(PROJECT_ID, SUBSCRIPTION_ID)
