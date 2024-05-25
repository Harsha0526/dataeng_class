import requests
import json
import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from google.cloud import storage
from google.oauth2 import service_account
from concurrent.futures import ThreadPoolExecutor

class GoogleCloudManager:
    def __init__(self, project_id, topic_name, key_path, bucket_name):
        self.project_id = project_id
        self.topic_name = topic_name
        self.key_path = key_path
        self.bucket_name = bucket_name
        self.publisher = None
        self.topic_path = None
        self.storage_client = None
        self.bucket = None
        self.credentials = self._load_credentials()
        self._initialize_pubsub()
        self._initialize_storage()

    def _load_credentials(self):
        return service_account.Credentials.from_service_account_file(
            self.key_path,
            scopes=["https://www.googleapis.com/auth/pubsub", "https://www.googleapis.com/auth/cloud-platform"]
        )

    def _initialize_pubsub(self):
        self.publisher = pubsub_v1.PublisherClient(credentials=self.credentials)
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)

    def _initialize_storage(self):
        self.storage_client = storage.Client(credentials=self.credentials)
        self.bucket = self.storage_client.get_bucket(self.bucket_name)

class DataProcessor:
    def __init__(self, public_key_path):
        self.rsa_public_key = self._load_rsa_public_key(public_key_path)

    def _load_rsa_public_key(self, public_key_path):
        with open(public_key_path, "rb") as public_key_file:
            return RSA.import_key(public_key_file.read())

    def generate_aes_key(self):
        return get_random_bytes(16)  

    def encrypt_with_aes(self, data, key):
        cipher_aes = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        return cipher_aes.nonce, tag, ciphertext

    def encrypt_aes_key_with_rsa(self, aes_key):
        cipher_rsa = PKCS1_OAEP.new(self.rsa_public_key)
        return cipher_rsa.encrypt(aes_key)

class DataCollector:
    def __init__(self, data_processor, bucket_space_info_callback):
        self.data_processor = data_processor
        self.bucket_space_info_callback = bucket_space_info_callback

    def collect_bucket_space_info(self, vehicle_ids):
        total_bucket_space_original = 0
        total_bucket_space_compressed = 0
        total_bucket_space_encrypted = 0

        for vehicle_id in vehicle_ids:
            url = f"https://busdata.cs.pdx.edu/api/getBreadCrumbs?vehicle_id={vehicle_id}"
            response = requests.get(url)
            if response.status_code == 200:
                breadcrumbs = response.json()
                for breadcrumb in breadcrumbs:
                    original_size = len(json.dumps(breadcrumb))  
                    compressed_size = len(zlib.compress(json.dumps(breadcrumb).encode('utf-8'))) 
                    nonce, tag, ciphertext = self.data_processor.encrypt_with_aes(json.dumps(breadcrumb).encode('utf-8'), self.data_processor.generate_aes_key())
                    encrypted_size = len(nonce) + len(tag) + len(ciphertext)  

                    total_bucket_space_original += original_size
                    total_bucket_space_compressed += compressed_size
                    total_bucket_space_encrypted += encrypted_size

        return total_bucket_space_original, total_bucket_space_compressed, total_bucket_space_encrypted

def main():
    project_id = 'dataengineering-420401'
    topic_name = 'archivetest'
    key_path = "/home/harsha/dataengineering-420401-4dce86b55f22.json"
    bucket_name = "maintainence"
    public_key_path = "public_key.pem"

    google_cloud_manager = GoogleCloudManager(project_id, topic_name, key_path, bucket_name)
    data_processor = DataProcessor(public_key_path)
    data_collector = DataCollector(data_processor, google_cloud_manager)

    vehicle_ids = [3633, 3130, 3804, 3504, 3913, 3405, 3147, 3313, 3903, 3619, 4022, 3721, 3961, 3915, 3314, 4027, 3053, 3743,
                   4068, 3732, 4237, 3156, 4047, 3328, 3953, 3530, 3206, 4019, 3102, 3541, 3642, 3635, 4062, 3224, 3621, 3571, 3920,
                   3028, 4001, 3507, 4238, 3909, 3557, 3714, 3572, 4030, 3744, 99222, 3151, 3029, 2932, 3951, 4055, 4529, 3733, 3305,
                   2930, 4017, 3508, 4046, 3957, 3317, 3144, 3945, 4071, 3554, 3755, 4206, 3935, 4050, 3568, 3553, 3942, 3724, 2908,
                   4527, 2916, 3727, 3745, 3122, 3749, 4203, 4015, 3216, 3613, 3422, 3937, 3021, 3562, 3165, 3623, 3210, 3204, 3520,
                   3707, 4214, 2940, 4043, 3648]

    original_size, compressed_size, encrypted_size = data_collector.collect_bucket_space_info(vehicle_ids)

    # Convert bytes to KiBs
    original_size_kib = original_size / 1024
    compressed_size_kib = compressed_size / 1024
    encrypted_size_kib = encrypted_size / 1024

    # Print answers
    print("C. [MUST] Store Data to GCP Storage Bucket")
    print(f"{original_size_kib:.2f} KiBs")
    print()
    print("D. [SHOULD] Compress")
    print(f"{compressed_size_kib:.2f} KiBs")
    print()
    print("E. [SHOULD] Encrypt")
    print(f"{encrypted_size_kib:.2f} KiBs")

if __name__ == '__main__':
    main()
