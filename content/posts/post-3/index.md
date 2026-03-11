+++
title = 'Choosing a PRNG for Simulations'
date = 2024-03-15
draft = false
tags = ['rust', 'math', 'probability']
description = 'Why the default random number generator is often wrong for simulations, and how to pick a better one.'
math = true
+++

Monte Carlo algorithms live and die by their random number generators. A path tracer might draw billions of samples per frame; a physics simulation might run for millions of steps. Using a low-quality PRNG introduces correlations that cause systematic error in the output — error that looks like noise and is very hard to debug.

## What Makes a PRNG Bad

The oldest generators — linear congruential generators (LCGs) — compute each value as:

$$x_{n+1} = (ax_n + c) \bmod m$$

They are fast and tiny, but the low bits repeat with very short periods and successive values fall on a small number of hyperplanes in high-dimensional space. For 3D Monte Carlo sampling this is directly harmful: sample points cluster along planes instead of filling the domain uniformly.

The Mersenne Twister (MT19937) is far better and was the default in many languages for decades. It has a period of $2^{19937}-1$ and passes most statistical tests. But it has a 2.5 KB state, poor cache behavior, and is not particularly fast on modern hardware. For most simulations today it is not the best choice.

## Better Alternatives

**xoshiro256++** and **xoshiro256\*\*** are the current go-to generators for simulations that need both speed and quality. They have 256 bits of state, pass all known statistical tests, and produce 64-bit output in about 4 clock cycles:

```rust
use rand::SeedableRng;
use rand_xoshiro::Xoshiro256PlusPlus;

let mut rng = Xoshiro256PlusPlus::seed_from_u64(12345);
let sample: f64 = rng.gen();
```

**PCG64** is another strong choice. It is slightly slower than xoshiro but has a proven analysis and supports efficient jump-ahead (advancing the state by $n$ steps in $O(\log n)$ time), which is useful for parallel simulations where each thread needs an independent, non-overlapping stream.

## Seeding

Bad seeding ruins a good PRNG. Common mistakes:

- Seeding with the current time in seconds — two runs started in the same second produce identical output.
- Seeding with a small integer directly — most PRNG algorithms map similar seeds to similar initial states, causing the first few outputs to be correlated across runs.

The correct approach is to seed with 256 bits of OS entropy, which `rand` handles automatically:

```rust
// Good: seeds from OS entropy
let mut rng = Xoshiro256PlusPlus::from_entropy();

// Acceptable for reproducible runs: hash the seed first
let mut rng = Xoshiro256PlusPlus::seed_from_u64(
    std::hash::BuildHasher::hash_one(&std::collections::hash_map::RandomState::new(), seed)
);
```

## Parallel Sampling

Running multiple rendering threads each using the same seed produces correlated samples. Two patterns avoid this:

**Jump-ahead**: initialize one RNG, then jump it ahead by a fixed stride per thread. PCG64 supports this natively; for xoshiro, use the provided `jump()` method which advances the state by $2^{128}$ steps:

```rust
let mut rngs: Vec<_> = (0..num_threads).map(|_| {
    let r = rng.clone();
    rng.jump(); // advance base by 2^128 steps
    r
}).collect();
```

**Per-pixel seeding**: hash the pixel coordinates and sample index into a seed. This makes each pixel's samples independent regardless of thread assignment:

```rust
fn pixel_rng(x: u32, y: u32, sample: u32) -> Xoshiro256PlusPlus {
    let seed = (x as u64) ^ ((y as u64) << 16) ^ ((sample as u64) << 32);
    Xoshiro256PlusPlus::seed_from_u64(splitmix64(seed))
}

fn splitmix64(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94d049bb133111eb);
    x ^ (x >> 31)
}
```

`splitmix64` is a finalizer that turns a structured input (sequential integers) into a high-quality seed, avoiding the correlated-seed problem.

## Summary

For most simulation work: use xoshiro256++ from `rand_xoshiro`, seed from OS entropy, and use jump-ahead or per-pixel hashing for parallel streams. The upgrade from `thread_rng` (which wraps OS entropy directly, with syscall overhead) or from Mersenne Twister is worth it both for speed and for the absence of subtle low-dimensional correlations.
