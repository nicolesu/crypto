from typing import Optional, List
from hashlib import sha256

def verify(obj: str, proof: str, commitment: str) -> bool:
	current_hash = sha256(obj.encode()).hexdigest()
	for sibling in proof:
		if current_hash < sibling:
			current_hash = sha256((current_hash + sibling).encode()).hexdigest()
		else:
			current_hash = sha256((sibling + current_hash).encode()).hexdigest()
    
	return current_hash == commitment

	# raise NotImplementedError	

class MerkleTree:
	def __init__(self, leaves: List[str]):
		# initiate the bottom leve leaves
		self.leaves = [self.hash(obj) for obj in leaves]
		self.tree = []
		self.build_tree()
	
	def hash(self, data: str) -> str:
		return sha256(data.encode()).hexdigest()
	
	def build_tree(self):
		self.tree.append(self.leaves)
		current_level = self.leaves

		while len(current_level) > 1:
			if len(current_level) % 2 == 1:
				# if leave number is odd copied the last node
				current_level.append(current_level[-1]) 
            
			parent_level = []
			for i in range(0, len(current_level), 2):
				parent_level.append(self.hash(current_level[i] + current_level[i+1]))
            
			self.tree.append(parent_level)
			current_level = parent_level

	def get_root(self) -> str:
		# negative indexing -- find the last level which should  be the root
		return self.tree[-1][0] if self.tree else ""

	def get_leaf(self, index: int) -> Optional[str]:
		return self.leaves[index] if 0 <= index < len(self.leaves) else None

	def generate_proof(self, index: int) -> Optional[List[str]]:
		if index < 0 or index >= len(self.leaves):
			return None

		proof = []
		level_index = index
		for level in self.tree[:-1]:  # Exclude root level
			is_right = level_index % 2
			sibling_index = level_index - 1 if is_right else level_index + 1
            
			if sibling_index < len(level):
				proof.append(level[sibling_index])
			level_index //= 2

		return proof

class Prover:
	def __init__(self):
		self.merkle_tree : Optional[MerkleTree] = None
		pass
	
	# Build a merkle tree and return the commitment
	def build_merkle_tree(self, objects: List[str]) -> str:
		self.merkle_tree = MerkleTree(objects)
		return self.merkle_tree.get_root()
		# raise NotImplementedError

	def get_leaf(self, index: int) -> Optional[str]:
		return self.merkle_tree.get_leaf(index) if self.merkle_tree else None
		# raise NotImplementedError

	def generate_proof(self, index: int) -> Optional[str]:
		return self.merkle_tree.generate_proof(index) if self.merkle_tree else None
		# raise NotImplementedError