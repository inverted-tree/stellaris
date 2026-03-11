+++
title = 'Why Write a Ray Tracer?'
date = 2024-01-10
draft = false
tags = ['rust', 'graphics', 'math']
description = 'Motivation, goals, and the math foundations before writing a single line of code.'
+++

Ray tracing is one of those topics that sits at the intersection of physics, linear algebra, and software engineering in a way that feels almost magical when it first works. You write a few hundred lines of code, point a virtual camera at some spheres, and get a photorealistic image with shadows and reflections. This series documents building one from scratch.

## What We Are Building

The goal is a CPU-bound path tracer capable of rendering scenes with:

- Diffuse, metallic, and dielectric materials
- Point lights and area lights
- A bounding volume hierarchy (BVH) for scene acceleration
- Multi-threaded rendering using Rayon

No GPU, no CUDA, no fancy APIs. Just vectors, rays, and math.

## The Core Abstraction

Everything in a ray tracer starts with a `Ray`. A ray is just an origin point and a direction vector, parameterized by `t`:

```rust
#[derive(Clone, Copy, Debug)]
pub struct Ray {
    pub origin: Vec3,
    pub direction: Vec3,
}

impl Ray {
    pub fn new(origin: Vec3, direction: Vec3) -> Self {
        Self { origin, direction: direction.normalize() }
    }

    pub fn at(&self, t: f32) -> Vec3 {
        self.origin + t * self.direction
    }
}
```

The `at(t)` method gives you the point along the ray at parameter `t`. Intersection testing is entirely about finding the right value of `t`.

## Vector Math

All of this rests on three-component vectors. Rather than pulling in a dependency like `glam`, we'll implement a minimal `Vec3` type. The operations we need are:

- Component-wise addition, subtraction, and multiplication
- Dot product and cross product
- Length and normalization
- Reflection and refraction (for materials)

The dot product $\mathbf{a} \cdot \mathbf{b} = a_x b_x + a_y b_y + a_z b_z$ will come up constantly — it encodes the cosine of the angle between two unit vectors, which is fundamental to lighting calculations.

## Next Steps

In the next post we will implement the first working renderer: a simple sphere intersector that produces a color-by-normal image. No lighting yet, but it will prove all the plumbing works.
