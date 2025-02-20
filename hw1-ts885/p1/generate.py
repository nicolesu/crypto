from hashlib import sha256
import random
import secrets
import string


netid = "ts885" # change to your netid
k = 4
n = 28

# Put your solution generation code here

def generate_watermark(id):
    encoded_id = id.encode('utf-8')
    hashed_id = sha256(encoded_id)
    id_hex_digest = hashed_id.hexdigest()

    # print(id_hex_digest)
    watermark = id_hex_digest[:4]
    return watermark


def find_coins(k, n, watermark): 
    collide_map = {}
    while True:
        # Generate 6 random bytes
        random_bytes = secrets.token_bytes(6)
        random_hex = random_bytes.hex()
        # Generate preimage, 8 bytes total
        preimage = watermark + random_hex
        hashed_preimage = sha256(preimage.encode('utf-8')).hexdigest()

        short_hashed_preimage = hashed_preimage[:n // 4]
        
        # add to map and count 
        if short_hashed_preimage in collide_map:
            collide_map[short_hashed_preimage].append(preimage)
            if len(collide_map[short_hashed_preimage]) == k:
                return collide_map[short_hashed_preimage]
        else:
            collide_map[short_hashed_preimage] = [preimage]

def generate_coin_txt():
    watermark = generate_watermark(netid)
    print("wm: " + watermark)
    colliding_coins = find_coins(k, n, watermark)
    print("Colliding Coins:", colliding_coins)
    # write to coin.txt
    with open("coin.txt", "w") as f:
        for coin in colliding_coins:
            f.write(coin + "\n")

def generate_random_id():
    # pick 2 or 3 letters
    letters = random.choices(string.ascii_lowercase, k=random.choice([2, 3])) 
    # pick 1 to 10 digits 
    numbers = random.choices(string.digits, k=random.randint(1, 10)) 
    return "".join(letters + numbers)

def find_forged_id(watermark):
    attempts = 0
    while True:
        forged_id = generate_random_id()
        # check if it's the exact same netid
        if forged_id == netid:  
            continue

        forged_hash = sha256(forged_id.encode('utf-8')).hexdigest()
        if forged_hash[:4] == watermark:
            print(f"Found forged NetID after {attempts} attempts!")
            return forged_id
        
        attempts += 1
        # set a max attempt
        if attempts == 1000000000: 
            print(f"Tried 100000000 netids already ...")
            break

def generate_forged_watermark():
    watermark = generate_watermark(netid)
    print("wm: " + watermark)
    forged_nid = find_forged_id(watermark)
    print("Forged NetID:", forged_nid)

    # write to forged-watermark.txt
    with open("forged-watermark.txt", "w") as f:
        f.write(str(forged_nid) + "\n")
    
    return forged_nid

### find colliding coings and write to file
generate_coin_txt()

### find alternate id with the same watermark
forged_id = generate_forged_watermark()


# compare and validate
original_watermark = generate_watermark(netid)
forged_watermark = generate_watermark(forged_id)
print('original id: ' + netid + ', original watermark: ' + original_watermark)
print('forged id: ' + forged_id + ', forged watermark: ' + forged_watermark)
