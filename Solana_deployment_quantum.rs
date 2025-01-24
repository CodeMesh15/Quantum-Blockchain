use std::collections::HashMap;
use rand::Rng;
use sha2::{Sha256, Digest};
use serde::{Serialize, Deserialize};
use chrono::Utc;

#[derive(Debug, Serialize, Deserialize)]
struct BlockHeader {
    previous_hash: String,
    timestamp: i64,
    block_hash: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct BlockBody {
    transactions: Vec<Transaction>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Block {
    header: BlockHeader,
    body: BlockBody,
}

#[derive(Debug, Clone)]
struct Node {
    id: usize,
    public_key: Vec<bool>,
    private_key: Vec<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Transaction {
    sender: usize,
    message: String,
    signature: Vec<bool>,
}

#[derive(Debug)]
struct QuantumBlockchain {
    blockchain: Vec<Block>,
    nodes: HashMap<usize, Node>,
}

impl QuantumBlockchain {
    fn new(num_nodes: usize) -> Self {
        let mut nodes = HashMap::new();
        for id in 0..num_nodes {
            let (private_key, public_key) = QuantumBlockchain::generate_keys();
            nodes.insert(id, Node { id, public_key, private_key });
        }
        QuantumBlockchain { blockchain: Vec::new(), nodes }
    }

    fn generate_keys() -> (Vec<bool>, Vec<bool>) {
        let mut rng = rand::thread_rng();
        let private_key: Vec<bool> = (0..10).map(|_| rng.gen_bool(0.5)).collect();
        let public_key = private_key.clone(); // In classical simulation, keys are the same.
        (private_key, public_key)
    }

    fn sign_message(message: &str, private_key: &Vec<bool>) -> Vec<bool> {
        let mut signature = vec![];
        for (i, bit) in message.bytes().enumerate() {
            let key_bit = private_key[i % private_key.len()];
            signature.push((bit % 2 == 1) ^ key_bit); // XOR operation for simplicity.
        }
        signature
    }

    fn verify_signature(message: &str, signature: &Vec<bool>, public_key: &Vec<bool>) -> bool {
        for (i, bit) in message.bytes().enumerate() {
            let key_bit = public_key[i % public_key.len()];
            let expected_bit = (bit % 2 == 1) ^ key_bit;
            if signature[i] != expected_bit {
                return false;
            }
        }
        true
    }

    fn create_block(&mut self, transactions: Vec<Transaction>, previous_hash: String) -> Block {
        let timestamp = Utc::now().timestamp();
        let body = BlockBody { transactions };
        let mut hasher = Sha256::new();
        let body_data = serde_json::to_string(&body).unwrap();
        hasher.update(body_data.as_bytes());
        hasher.update(previous_hash.as_bytes());
        let hash_result = hasher.finalize();
        let block_hash = format!("{:x}", hash_result);

        Block {
            header: BlockHeader {
                previous_hash,
                timestamp,
                block_hash,
            },
            body,
        }
    }

    fn add_block(&mut self, block: Block) {
        self.blockchain.push(block);
    }

    fn simulate_voting(&self, num_candidates: usize) -> Vec<usize> {
        let mut scores = vec![0; num_candidates];
        let mut rng = rand::thread_rng();

        for _ in &self.nodes {
            let preferences: Vec<usize> = (0..num_candidates).collect();
            let mut ranked_candidates = preferences.clone();
            ranked_candidates.shuffle(&mut rng);

            for (rank, candidate) in ranked_candidates.iter().enumerate() {
                scores[*candidate] += num_candidates - rank;
            }
        }

        let mut candidate_scores: Vec<(usize, usize)> = scores.into_iter().enumerate().collect();
        candidate_scores.sort_by(|a, b| b.1.cmp(&a.1));
        candidate_scores.into_iter().map(|(candidate, _)| candidate).collect()
    }

    fn display_blockchain(&self) {
        for (i, block) in self.blockchain.iter().enumerate() {
            println!("Block {}: {:?}", i, block);
        }
    }
}

fn main() {
    let mut blockchain = QuantumBlockchain::new(10);

    // Simulate voting
    let selected_nodes = blockchain.simulate_voting(5);
    println!("Selected Witness Nodes: {:?}", selected_nodes);

    // Generate sample transactions
    let transaction_1 = Transaction {
        sender: 0,
        message: "Message 101".to_string(),
        signature: QuantumBlockchain::sign_message("Message 101", &blockchain.nodes[&0].private_key),
    };
    let transaction_2 = Transaction {
        sender: 1,
        message: "Message 110".to_string(),
        signature: QuantumBlockchain::sign_message("Message 110", &blockchain.nodes[&1].private_key),
    };

    // Validate and create a block
    let transactions = vec![transaction_1.clone(), transaction_2.clone()];
    let valid_transactions: Vec<Transaction> = transactions
        .into_iter()
        .filter(|tx| {
            QuantumBlockchain::verify_signature(
                &tx.message,
                &tx.signature,
                &blockchain.nodes[&tx.sender].public_key,
            )
        })
        .collect();

    let previous_hash = if blockchain.blockchain.is_empty() {
        "0".to_string()
    } else {
        blockchain.blockchain.last().unwrap().header.block_hash.clone()
    };

    let new_block = blockchain.create_block(valid_transactions, previous_hash);
    blockchain.add_block(new_block);

    // Display the blockchain
    blockchain.display_blockchain();
}
