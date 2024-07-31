use std::error::Error;

use fasthash::murmur3;
use fixedbitset::FixedBitSet;

fn split_u128(value: u128) -> (u64, u64) {
    let high = (value >> 64) as u64;
    let low = value as u64;
    (high, low)
}

pub struct BloomFilter {
    m: usize,
    k: usize,
    bitset: FixedBitSet,
}

impl BloomFilter {
    pub fn new(m: usize, k: usize) -> Self {
        Self {
            m: m.max(1),
            k: k.max(1),
            bitset: FixedBitSet::with_capacity(m),
        }
    }

    fn compute_hash(data: &[u8]) -> [u64; 4] {
        let hash_1 = murmur3::hash128(data);
        let hash_2 = murmur3::hash128(&[data, &[1]].concat());

        let (hash_1_high, hash_1_low) = split_u128(hash_1);
        let (hash_2_high, hash_2_low) = split_u128(hash_2);

        [hash_1_low, hash_1_high, hash_2_low, hash_2_high]
    }

    fn get_location(&self, h: [u64; 4], i: usize) -> usize {
        let ii = i as u64;
        let index = 2 + (((i + (i % 2)) % 4) / 2);
        let result = h[i % 2].wrapping_add(ii.wrapping_mul(h[index]));
        (result % (self.m as u64)) as usize
    }

    /// Cap returns the capacity, _m_, of a Bloom filter
    pub fn capacity(&self) -> usize {
        self.m
    }

    pub fn k(&self) -> usize {
        self.k
    }

    pub fn bitset(&self) -> &FixedBitSet {
        &self.bitset
    }

    pub fn insert(&mut self, data: &[u8]) -> &mut Self {
        let h = Self::compute_hash(data);

        for i in 0..self.k {
            let loc = self.get_location(h, i);
            self.bitset.insert(loc);
        }

        self
    }

    pub fn contains(&self, data: &[u8]) -> bool {
        let h = Self::compute_hash(data);
        println!("hash is {:?}", h);
        for i in 0..self.k {
            let loc = self.get_location(h, i);
            if !self.bitset.contains(loc) {
                return false;
            }
        }
        true
    }

    pub fn clear(&mut self) -> &mut Self {
        self.bitset.clear();
        self
    }

    pub fn union(&mut self, other: &Self) -> Result<(), Box<dyn Error>> {
        if self.m != other.m {
            return Err(format!("m's don't match: {} != {}", self.m, other.m).into());
        }

        if self.k != other.k {
            return Err(format!("k's don't match: {} != {}", self.k, other.k).into());
        }

        self.bitset.union_with(&other.bitset);
        Ok(())
    }
}

impl Clone for BloomFilter {
    fn clone(&self) -> Self {
        Self {
            m: self.m,
            k: self.k,
            bitset: self.bitset.clone(),
        }
    }
}

#[test]
fn test_new() {
    let bf = BloomFilter::new(100, 3);

    assert_eq!(bf.capacity(), 100);
    assert_eq!(bf.k(), 3);
    assert_eq!(bf.bitset().len(), 100);
}

#[test]
fn test_insert() {
    let mut bf = BloomFilter::new(32, 3);

    assert_eq!(bf.bitset().to_string(), "00000000000000000000000000000000");

    bf.insert(b"hello");
    assert_eq!(bf.bitset().to_string(), "00100000000000000000010000100000");

    bf.insert(b"world");
    assert_eq!(bf.bitset().to_string(), "00101000001000000000010000100010");
}

#[test]
fn test_contains() {
    let mut bf = BloomFilter::new(128, 3);

    assert!(!bf.contains(b"hello"));
    assert!(!bf.contains(b"world"));

    bf.insert(b"hello");
    assert!(bf.contains(b"hello"));

    bf.insert(b"world");
    assert!(bf.contains(b"world"));

    assert!(!bf.contains(b"foo"));

    bf.clear();
    assert!(!bf.contains(b"hello"));
    assert!(!bf.contains(b"world"));
}

#[test]
fn test_union() {
    let mut bf1 = BloomFilter::new(32, 3);
    bf1.insert(b"hello");
    assert_eq!(bf1.bitset().to_string(), "00100000000000000000010000100000");

    let mut bf2 = BloomFilter::new(32, 3);
    bf2.insert(b"world");

    bf1.union(&bf2).unwrap();

    assert_eq!(bf1.bitset().to_string(), "00101000001000000000010000100010");
}
