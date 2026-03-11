+++
title = 'Floating-Point Pitfalls in Graphics Code'
date = 2024-01-10
draft = false
tags = ['rust', 'graphics', 'math']
description = 'The subtle ways IEEE 754 arithmetic breaks graphics algorithms, and practical defenses against them.'
math = true
+++

Graphics code is full of floating-point arithmetic, and floating-point arithmetic is full of surprises. Most of the time the approximations are harmless. Occasionally they cause a ray to miss a surface it should hit, a normal to point inward when it should point out, or a color value to go subtly negative and corrupt the entire image.

## The Epsilon Trap

The most common mistake is writing `a == b` for two floats that were computed differently. A textbook fix is `abs(a - b) < epsilon`, but choosing epsilon is harder than it looks.

A fixed epsilon like `1e-6` fails at large scales — two points a kilometer apart might differ by more than that due to accumulated error — and it is overly strict at small scales. The correct tool is a *relative* epsilon:

```rust
fn approx_eq(a: f32, b: f32, rel_tol: f32) -> bool {
    let diff = (a - b).abs();
    let mag  = a.abs().max(b.abs());
    diff <= rel_tol * mag
}
```

But even this breaks down near zero, where both `a` and `b` can be tiny and `mag` becomes meaninglessly small. For geometry, the better question is usually not "are these equal" but "is this value within the valid range I expect" — which sidesteps the comparison entirely.

## Catastrophic Cancellation

When two nearly-equal numbers are subtracted, significant digits vanish. The ray-sphere discriminant $b^2 - 4ac$ is a classic example: if $b^2 \approx 4ac$, the result loses many bits of precision.

The standard fix is the half-$b$ reformulation. Instead of:

$$t = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

factor out a 2 from $b = 2h$ and compute:

$$t = \frac{-h \pm \sqrt{h^2 - ac}}{a}$$

The subtraction still happens, but the operands are smaller and the result is the same number of ULPs away from the true answer.

## NaN Propagation

NaN is contagious: any arithmetic involving a NaN produces another NaN. In a path tracer this means one bad sample silently corrupts the accumulation buffer for that pixel. The symptom is a cluster of black or white pixels with no error message.

```rust
fn safe_sqrt(x: f32) -> f32 {
    // Negative inputs from numerical error near zero
    x.max(0.0).sqrt()
}

fn is_valid_color(c: Vec3) -> bool {
    c.x.is_finite() && c.y.is_finite() && c.z.is_finite()
        && c.x >= 0.0 && c.y >= 0.0 && c.z >= 0.0
}
```

Inserting `is_valid_color` guards at sample accumulation and clamping the square root input to zero catches the two most common sources of NaN in renderer code.

## Self-Intersection Bias

After a ray hits a surface, the next ray must start slightly above the surface — otherwise floating-point error places the origin below the surface and it immediately re-intersects at $t \approx 0$. A naive fix is to add a small offset along the normal:

```rust
let origin = hit.point + hit.normal * 1e-4;
```

But `1e-4` is wrong at two ends of the scale: too small for geometry far from the origin (where float spacing is large), too large for tiny geometry (where it visibly lifts the ray off the surface). The correct approach, described by Carsten Wächter and Nikolaus Binder, offsets by a fixed number of ULPs rather than a fixed world-space distance. Rust makes this straightforward:

```rust
fn offset_ray_origin(p: Vec3, n: Vec3) -> Vec3 {
    const N: i32 = 4;
    Vec3::new(
        f32::from_bits((p.x.to_bits() as i32 + if p.x * n.x >= 0.0 { N } else { -N }) as u32),
        f32::from_bits((p.y.to_bits() as i32 + if p.y * n.y >= 0.0 { N } else { -N }) as u32),
        f32::from_bits((p.z.to_bits() as i32 + if p.z * n.z >= 0.0 { N } else { -N }) as u32),
    )
}
```

This nudges each component by exactly 4 ULPs in the direction that moves away from the surface, regardless of the scale of the coordinates.

## Takeaway

Floating-point errors in graphics are rarely random noise — they have structure. Knowing which operations lose precision (subtraction of nearly-equal values, division near zero, comparison for equality) lets you audit the hot paths in a renderer and replace the fragile operations before they cause artifacts.
