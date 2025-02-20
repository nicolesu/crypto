from hashlib import sha256
import secrets


netid = "ts885" # change to your netid
# testid = "af535"
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

watermark = generate_watermark(netid)
print("wm: " + watermark)

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

colliding_coins = find_coins(k, n, watermark)
print("Colliding Coins:", colliding_coins)

# write to coin.txt
with open("coin.txt", "w") as f:
    for coin in colliding_coins:
        f.write(coin + "\n")