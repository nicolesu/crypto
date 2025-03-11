from abc import ABC, abstractmethod # We want to make Block an abstract class; either a PoW or PoA block
import blockchain
from blockchain.util import sha256_2_string, encode_as_str
import time
import persistent
from blockchain.util import nonempty_intersection
from math import log2, ceil

class Block(ABC, persistent.Persistent):

    def __init__(self, height, transactions, parent_hash, is_genesis=False, timestamp=time.time(),
            target=None, merkle=None, seal_data=0):
        """ Creates a block template (unsealed).

        Args:
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            parent_hash (str): the hash of the parent block in the blockchain.
            is_genesis (bool, optional): True only if the block is a genesis block.

        Attributes:
            parent_hash (str): the hash of the parent block in blockchain.
            height (int): height of the block in the chain (# of blocks between block and genesis).
            transactions (:obj:`list` of :obj:`Transaction`): ordered list of transactions in the block.
            timestamp (int): Unix timestamp of the block
            target (int): Target value for the block's seal to be valid (different for each seal mechanism)
            is_genesis (bool): True only if the block is a genesis block (first block in the chain).
            merkle (str): Merkle hash of the list of transactions in a block, uniquely identifying the list.
            seal_data (int): Seal data for block (in PoW this is the nonce satisfying the PoW puzzle; in PoA, the signature of the authority"
            hash (str): Hex-encoded SHA256^2 hash of the block header (self.header())
        """
        self.parent_hash = parent_hash
        self.height = height
        self.transactions = transactions
        self.timestamp = timestamp
        self.target = target
        self.is_genesis = is_genesis
        self.merkle = merkle
        self.seal_data = seal_data
        if target == None:
            self.target = self.calculate_appropriate_target()
        if merkle == None:
            self.merkle = self.calculate_merkle_root()
        self.hash = self.calculate_hash() # keep track of hash for caching purposes

    def calculate_merkle_root(self):
        """ Gets the Merkle root hash for a given list of transactions.

        This method is incomplete!  Right now, it only hashes the
        transactions together, which does not enable the same type
        of lite client support a true Merkle hash would.
        You do not need to complete this except for the bonus question.

        Returns:
            str: Merkle hash of the list of transactions in a block, uniquely identifying the list.
        """

        if len(self.transactions) == 0:
            return sha256_2_string("")
        elif len(self.transactions) == 1:
            return sha256_2_string(str(self.transactions[0]))
        else:
            total = len(self.transactions)
            levels = 1 + ceil(log2(total))
            treenodes = [None] * levels
            for i in range(levels):
                treenodes[i] = [None] * (1 << i)

            level = levels - 1
            for i in range(1 << level):
                if i < len(self.transactions):
                    treenodes[level][i] = sha256_2_string(str(self.transactions[i]))
                else:
                    treenodes[level][i] = sha256_2_string("")
            while level > 0:
                level = level - 1
                for i in range(1 << level):
                    treenodes[level][i] = sha256_2_string(treenodes[level + 1][2*i] + treenodes[level + 1][2*i + 1])

            return treenodes[0][0]

    def unsealed_header(self):
        """ Computes the header string of a block (the component that is sealed by mining).

        Returns:
            str: String representation of the block header without the seal.
        """
        return encode_as_str([self.height, self.timestamp, self.target, self.parent_hash, self.is_genesis, self.merkle], sep='`')

    def header(self):
        """ Computes the full header string of a block after mining (includes the seal).

        Returns:
            str: String representation of the block header.
        """
        return encode_as_str([self.unsealed_header(), self.seal_data], sep='`')

    def calculate_hash(self):
        """ Get the SHA256^2 hash of the block header.

        Returns:
            str: SHA256^2 hash of self.header()
        """
        return sha256_2_string(str(self.header()))

    def __repr__(self):
        """ Get a full representation of a block as string, for debugging purposes; includes all transactions.

        Returns:
            str: Full and unique representation of a block and its transactions.
        """
        return encode_as_str([self.header(), "!".join([str(tx) for tx in self.transactions])], sep="`")

    def set_seal_data(self, seal_data):
        """ Adds seal data to a block, recomputing the block's hash for its changed header representation.
        This method should never be called after a block is added to the blockchain!

        Args:
            seal_data (int): The seal data to set.
        """
        self.seal_data = seal_data
        self.hash = self.calculate_hash()

    def is_valid(self):
        """ Check whether block is fully valid according to block rules.

        Includes checking for no double spend, that all transactions are valid, that all header fields are correctly
        computed, etc.

        Returns:
            bool, str: True if block is valid, False otherwise plus an error or success message.
        """

        chain = blockchain.chain # This object of type Blockchain may be useful

        # Placeholder for (1a)

        # (checks that apply to all blocks)
        # Check that Merkle root calculation is consistent with transactions in block (use the calculate_merkle_root function) [test_rejects_invalid_merkle]
        # On failure: return False, "Merkle root failed to match"
        res = self.calculate_merkle_root() == self.merkle
        if not res:
            return False, "Merkle root failed to match"

        # Check that block.hash is correctly calculated [test_rejects_invalid_hash]
        # On failure: return False, "Hash failed to match"
        res = self.calculate_hash() == self.hash
        if not res:
            return False, "Hash failed to match"

        # Check that there are at most 900 transactions in the block [test_rejects_too_many_txs]
        # On failure: return False, "Too many transactions"
        res = len(self.transactions) <= 900
        if not res:
            return False, "Too many transactions"

        # (checks that apply to genesis block)
        if self.is_genesis:
            # Check that height is 0 and parent_hash is "genesis" [test_invalid_genesis]
            # On failure: return False, "Invalid genesis"
            res = self.height == 0 and self.parent_hash == "genesis"
            if not res:
                return False, "Invalid genesis"

        # (checks that apply only to non-genesis blocks)
        else:
            # Check that parent exists (you may find chain.blocks helpful) [test_nonexistent_parent]
            # On failure: return False, "Nonexistent parent"
            res = self.parent_hash in chain.blocks
            if not res:
                return False, "Nonexistent parent"

            # Check that height is correct w.r.t. parent height [test_bad_height]
            # On failure: return False, "Invalid height"
            res = self.height == chain.blocks[self.parent_hash].height + 1
            if not res:
                return False, "Invalid height"

            # Check that timestamp is non-decreasing [test_bad_timestamp]
            # On failure: return False, "Invalid timestamp"
            res = self.timestamp >= chain.blocks[self.parent_hash].timestamp
            if not res:
                return False, "Invalid timestamp"

            # Check that seal is correctly computed and satisfies "target" requirements; use the provided seal_is_valid method [test_bad_seal]
            # On failure: return False, "Invalid seal"
            res = self.seal_is_valid()
            if not res:
                return False, "Invalid seal"

            # Check that all transactions within are valid (use tx.is_valid) [test_malformed_txs]
            # On failure: return False, "Malformed transaction included"
            res = all(tx.is_valid() for tx in self.transactions)
            if not res:
                return False, "Malformed transaction included"

            # Check that for every transaction
            tx_hash_to_tx = defaultdict(list)
            for tx in self.transactions:
                tx_hash_to_tx[tx.hash].append(tx)
            for tx in self.transactions:
                # the transaction has not already been included on a block on the same blockchain as this block [test_double_tx_inclusion_same_chain]
                # (or twice in this block; you will have to check this manually) [test_double_tx_inclusion_same_block]
                # (you may find chain.get_chain_ending_with and chain.blocks_containing_tx and util.nonempty_intersection useful)
                # On failure: return False, "Double transaction inclusion"
                curr_chain = chain.get_chain_ending_with(self.parent_hash)
                blocks_containing_tx = chain.blocks_containing_tx.get(tx.hash, None)
                if blocks_containing_tx is None:
                    # check if the tx is in the current block
                    if len(tx_hash_to_tx[tx.hash]) > 1:
                        return False, "Double transaction inclusion"
                else:
                    if nonempty_intersection(curr_chain, blocks_containing_tx):
                        return False, "Double transaction inclusion"

                # for every input ref in the tx
                sender = tx.outputs[0].sender
                for tx_input_ref in tx.input_refs:
                    # (you may find the string split method for parsing the input into its components)
                    input_ref = tx_input_ref.split(":")[0]
                    idx = int(tx_input_ref.split(":")[1])

                    # each input_ref is valid (aka corresponding transaction can be looked up in its holding transaction) [test_failed_input_lookup]
                    # (you may find chain.all_transactions useful here)
                    # On failure: return False, "Required output not found"
                    if input_ref not in chain.all_transactions:
                        # if the input_ref is in current block, then it is valid, else it is not
                        if input_ref not in tx_hash_to_tx:
                            return False, "Required output not found"
                    else:
                        if idx >= len(chain.all_transactions[input_ref].outputs):
                            return False, "Required output not found"


                    # every input was sent to the same user (would normally carry a signature from this user; we leave this out for simplicity) [test_user_consistency]
                    # On failure: return False, "User inconsistencies"
                    _input = chain.all_transactions[input_ref].outputs[idx] if input_ref in chain.all_transactions else tx_hash_to_tx[input_ref][0].outputs[idx]
                    res = _input.receiver == sender
                    if not res:
                        return False, "User inconsistencies"

                    # no input_ref has been spent in a previous block on this chain [test_doublespent_input_same_chain]
                    # (or in this block; you will have to check this manually) [test_doublespent_input_same_block]
                    # (you may find nonempty_intersection and chain.blocks_spending_input helpful here)
                    # On failure: return False, "Double-spent input"
                    blocks = chain.blocks_spending_input.get(tx_input_ref, None)
                    if blocks is not None:
                        res = not nonempty_intersection(curr_chain, blocks)
                        if not res:
                            return False, "Double-spent input"
                    for tx_in_same_block in self.transactions:
                        if tx_in_same_block.hash != tx.hash:
                            for tx_input_ref_in_same_block in tx_in_same_block.input_refs:
                                if tx_input_ref_in_same_block == tx_input_ref:
                                    return False, "Double-spent input"

                    # each input_ref points to a transaction on the same blockchain as this block [test_input_txs_on_chain]
                    # (or in this block; you will have to check this manually) [test_input_txs_in_block]
                    # (you may find chain.blocks_containing_tx.get and nonempty_intersection as above helpful)
                    # On failure: return False, "Input transaction not found"

                    # first, check if the input transaction is in the current block, then check if it is in the current chain
                    if input_ref not in [tx_in_same_block.hash for tx_in_same_block in self.transactions]:
                        blocks = chain.blocks_containing_tx.get(input_ref, [])
                        if not nonempty_intersection(curr_chain, blocks):
                            return False, "Input transaction not found"

                # for every output in the tx
                for tx_output in tx.outputs:
                    # every output was sent from the same user (would normally carry a signature from this user; we leave this out for simplicity)
                    # (this MUST be the same user as the outputs are locked to above) [test_user_consistency]
                    # On failure: return False, "User inconsistencies"
                     if tx_output.sender != sender:
                        return False, "User inconsistencies"

                # the sum of the input values is at least the sum of the output values (no money created out of thin air) [test_no_money_creation]
                # On failure: return False, "Creating money"
                input_sum = 0
                for tx_input_ref in tx.input_refs:
                    # two cases: input_ref is either in the current chain or in the current block
                    if tx_input_ref.split(":")[0] in chain.all_transactions:
                        input_sum += chain.all_transactions[tx_input_ref.split(":")[0]].outputs[int(tx_input_ref.split(":")[1])].amount
                    else:
                        input_sum += tx_hash_to_tx[tx_input_ref.split(":")[0]][0].outputs[int(tx_input_ref.split(":")[1])].amount

                output_sum = sum(tx_output.amount for tx_output in tx.outputs)
                if input_sum < output_sum:
                    return False, "Creating money"

        return True, "All checks passed"


    # ( these just establish methods for subclasses to implement; no need to modify )
    @abstractmethod
    def get_weight(self):
        """ Should be implemented by subclasses; gives consensus weight of block. """
        pass

    @abstractmethod
    def calculate_appropriate_target(self):
        """ Should be implemented by subclasses; calculates correct target to use in block. """
        pass

    @abstractmethod
    def seal_is_valid(self):
        """ Should be implemented by subclasses; returns True iff the seal_data creates a valid seal on the block. """
        pass
