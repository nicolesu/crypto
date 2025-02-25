import string
import random
import hashlib

# return the hash of a string
def SHA(s: string) -> string:
    return hashlib.sha256(s.encode()).hexdigest()

# transfer a hex string to integer
def toDigit(s: string) -> int:
    return int(s, 16)

# generate 2^d (si^{-1}, si) pairs based on seed r
def KeyPairGen(d: int, r: int) -> dict:
    pairs = {}
    random.seed(r)
    for i in range(1 << d):
        cur = random.randbytes(32).hex()
        while cur in pairs:
            cur = random.randbytes(32).hex()
        pairs[cur] = SHA(cur)
    return pairs


class MTSignature:
    def __init__(self, d, k):
        self.d = d
        self.k = k
        self.treenodes = [None] * (d+1)
        for i in range(d+1):
            self.treenodes[i] = [None] * (1 << i)
        self.sk = [None] * (1 << d)
        self.pk = None # same as self.treenodes[0][0]


    # Populate the fields self.treenodes, self.sk and self.pk. Returns self.pk.
    def KeyGen(self, seed: int) -> string:
        key_pairs = KeyPairGen(self.d, seed)
        self.sk = list(key_pairs.keys())
        leaves = list(key_pairs.values())
        # populate the leaf level
        self.treenodes[self.d] = leaves
        
         #populate the rest of the levels bottom up
        for level in range(self.d -1, -1, -1):
            for i in range(2 **  level):
                left = self.treenodes[level+1][2*i]
                right = self.treenodes[level+1][2*i+1]
                # first convert i into 256 bit binary string
                self.treenodes[level][i] = SHA(format(i, "b").zfill(256)+ left + right)

        self.pk = self.treenodes[0][0]
        return self.pk
        # raise NotImplementedError

    # Returns the path SPj for the index j
    # The order in SPj follows from the leaf to the root.
    def Path(self, j: int) -> string:
        path = []
        position = j
        for level in range(self.d, 0, -1):
            is_right = position % 2
            sibling_index = position - 1 if is_right else position + 1
            path.append(self.treenodes[level][sibling_index])
            # move up the level 
            position //= 2
        #print(path)
        return ''.join(path)
       # raise NotImplementedError

    # Returns the signature. The format of the signature is as follows: ([sigma], [SP]).
    # The first is a sequence of sigma values and the second is a list of sibling paths.
    # Each sibling path is in turn a d-length list of tree node values. 
    # All values are 64 bytes. Final signature is a single string obtained by concatentating all values.
    def Sign(self, msg: string) -> string:
        indices = []
        for i in range(1, self.k + 1):
            # compute Zj
            combined_string = format(i, "b").zfill(256) + msg
            hashed_value = SHA(combined_string)
            digit_value = toDigit(hashed_value)
            # convert hexadecimal string to integer before computing mod
            index = digit_value % (2** self.d)
             #index = hashed_value % (2** self.d)
            indices.append(index)
        
        sigma = []
        paths = []
        for  i in indices:
            sigma.append(self.sk[i])
            paths.append(self.Path(i))
        
        # return the concactenated string
        return ''.join(sigma) + ''.join([''.join(p) for p in paths])
       # return NotImplementedError
