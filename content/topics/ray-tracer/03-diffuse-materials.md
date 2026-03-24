+++
title = 'Diffuse Materials and Monte Carlo Sampling'
date = 2024-02-07
draft = false
tags = ['rust', 'graphics', 'math', 'probability']
math = true
description = 'Implementing Lambertian diffuse shading using Monte Carlo integration and random hemisphere sampling.'
+++

Diffuse surfaces scatter incoming light in all directions roughly equally. The physically correct model is Lambertian reflectance, where the probability of scattering in a given direction is proportional to the cosine of the angle with the surface normal.

## Monte Carlo Integration

We cannot analytically integrate over all possible incoming light directions, so we use Monte Carlo sampling: pick a random direction, trace a ray in that direction, and average many samples. The expected value converges to the true integral as sample count increases.

For a Lambertian surface, we want to sample directions with probability proportional to $\cos\theta$ where $\theta$ is the angle from the normal. The trick is to pick a random point on the unit sphere and add it to the surface normal:

```rust
fn random_in_unit_sphere(rng: &mut impl Rng) -> Vec3 {
    loop {
        let p = Vec3::new(
            rng.gen_range(-1.0..1.0),
            rng.gen_range(-1.0..1.0),
            rng.gen_range(-1.0..1.0),
        );
        if p.length_squared() < 1.0 {
            return p;
        }
    }
}

pub fn scatter_lambertian(
    hit: &HitRecord,
    rng: &mut impl Rng,
) -> Option<(Ray, Vec3)> {
    let scatter_direction = hit.normal + random_in_unit_sphere(rng).normalize();

    // Catch degenerate scatter direction (near-zero vector)
    let scatter_direction = if scatter_direction.near_zero() {
        hit.normal
    } else {
        scatter_direction
    };

    let scattered = Ray::new(hit.point, scatter_direction);
    let attenuation = /* material albedo color */;
    Some((scattered, attenuation))
}
```

## Gamma Correction

Raw linear output looks too dark because monitors apply a gamma curve ($\gamma \approx 2.2$). We store linear radiance values but must gamma-encode before writing pixels:

```rust
fn linear_to_gamma(linear: f32) -> f32 {
    if linear > 0.0 { linear.sqrt() } else { 0.0 }
}

fn write_pixel(color: Vec3, samples: u32) -> [u8; 3] {
    let scale = 1.0 / samples as f32;
    [
        (linear_to_gamma(color.x * scale) * 255.99) as u8,
        (linear_to_gamma(color.y * scale) * 255.99) as u8,
        (linear_to_gamma(color.z * scale) * 255.99) as u8,
    ]
}
```

Using `sqrt` as the gamma function is an approximation of $x^{1/2.2}$, but it is close enough and avoids a `powf` call in the hot path.

## Recursion Depth

The path tracer recurses: a scattered ray may itself bounce off another surface. Without a depth limit, this recurses infinitely. In practice, each bounce attenuates the energy, so the contribution of deep bounces becomes negligible. We cap at a depth of around 50 and return black when exceeded.

The full rendering loop with per-pixel sampling and depth limiting is the foundation that all future material types will build on.
