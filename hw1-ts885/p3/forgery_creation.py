import random
import string
from signature import MTSignature

d = 10
k = 2
r = 2023
m = "I am hungry"

def FindForgery(d: int, k: int, r: int, m: string):

    S3 = MTSignature(d, k)
    S3.KeyGen(r)
    signature = S3.Sign(m)

    characters = string.ascii_letters + string.digits + " .,!?"

    # Word bank for sentence construction
    subjects = ["Nicole", "A dog", "My friend", "The scientist", "That girl"]
    verbs = ["jumps", "runs", "sleeps", "thinks", "writes", "eats"]
    objects = ["on the couch", "in the lab", "with excitement", "at home", "in the park"]

    # try grammatically correct sentence attempt
    while True:
        m_prime = f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}."
        if m_prime != m and S3.Sign(m_prime) == signature:
            break
        
    # # Find another message with the same signature
    # while True:
    #     m_prime = ''.join(random.choices(characters, k=len(m)))
    #     if m_prime != m and S3.Sign(m_prime) == signature:
    #         break
        
    with open("forgery.txt", "w") as f:
        f.write(m + "\n" + m_prime)

FindForgery(d, k, r, m)

def ComputeDoubleSignature():
    target_prob = 0.5
    n = 200  
    # just a starting point
    d = 1
    while (n ** 2) / (2 ** (d + 1)) >= target_prob:
        d += 1
        
    with open("double.txt", "w") as f:
        f.write(f"Minimum d for collision probability < 50%: {d}\n")

# ComputeDoubleSignature()
