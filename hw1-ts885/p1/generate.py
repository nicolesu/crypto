from hashlib import sha256
import random
import secrets


netid = "ts885" # change to your netid
testid = "af535"
testforgedid = "qn00061"

# Put your solution generation code here

encoded_netid = testid.encode('ascii')
print(encoded_netid)
def hash_to_bin(s):
    return bin(int(sha256(s).hexdigest(), base=16)).lstrip('0b').zfill(256)

w = hash_to_bin(encoded_netid )[:16]
print(w)


def generate_watermark(id):
    encoded_id = id.encode('utf-8')
    hashed_id = sha256(encoded_id)
    id_hex_digest = hashed_id.hexdigest()

    # print(id_hex_digest)
    watermark = id_hex_digest[:4]
    print(watermark)
    return watermark


def find_forged(watermark):
    seen_hashes = {}
    max_attempts = 100000  # Limit the number of attempts to avoid infinite loops

    for i in range(max_attempts):
        # Generate a random string of characters
        random_string1 = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=20))
        hash_value1 = sha256(random_string1.encode()).hexdigest()
        truncated_hash1 = hash_value1[:4]  # Take only the necessary hex characters

        if truncated_hash1 in seen_hashes:
            random_string2 = seen_hashes[truncated_hash1]
            return random_string2, random_string1
        
        seen_hashes[truncated_hash1] = random_string1

    return None
