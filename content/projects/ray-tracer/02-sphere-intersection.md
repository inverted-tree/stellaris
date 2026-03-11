+++
title = 'Sphere Intersection and the First Image'
date = 2024-01-24
draft = false
tags = ['rust', 'graphics', 'math']
description = 'Deriving the ray-sphere intersection formula and rendering the first normal-mapped image.'
+++

The sphere is the "Hello World" of ray tracing because the intersection math is clean and closed-form. Given a ray $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$ and a sphere centered at $\mathbf{c}$ with radius $r$, we want the smallest positive $t$ where the ray touches the sphere surface.

## Derivation

A point $\mathbf{p}$ is on the sphere if $|\mathbf{p} - \mathbf{c}|^2 = r^2$. Substituting the ray:

$$|(\mathbf{o} + t\mathbf{d}) - \mathbf{c}|^2 = r^2$$

Let $\mathbf{oc} = \mathbf{o} - \mathbf{c}$. Expanding:

$$t^2(\mathbf{d} \cdot \mathbf{d}) + 2t(\mathbf{oc} \cdot \mathbf{d}) + (\mathbf{oc} \cdot \mathbf{oc} - r^2) = 0$$

This is a standard quadratic $at^2 + bt + c = 0$. The discriminant $b^2 - 4ac$ tells us whether the ray misses ($< 0$), grazes ($= 0$), or hits ($> 0$) the sphere.

## Implementation

```rust
pub struct Sphere {
    pub center: Vec3,
    pub radius: f32,
    pub material: Material,
}

impl Hittable for Sphere {
    fn hit(&self, ray: &Ray, t_min: f32, t_max: f32) -> Option<HitRecord> {
        let oc = ray.origin - self.center;
        let a = ray.direction.dot(ray.direction);
        let half_b = oc.dot(ray.direction);
        let c = oc.dot(oc) - self.radius * self.radius;
        let discriminant = half_b * half_b - a * c;

        if discriminant < 0.0 {
            return None;
        }

        let sqrt_d = discriminant.sqrt();
        let mut root = (-half_b - sqrt_d) / a;

        if root < t_min || root > t_max {
            root = (-half_b + sqrt_d) / a;
            if root < t_min || root > t_max {
                return None;
            }
        }

        let point = ray.at(root);
        let outward_normal = (point - self.center) / self.radius;

        Some(HitRecord {
            point,
            normal: outward_normal,
            t: root,
            front_face: ray.direction.dot(outward_normal) < 0.0,
            material: &self.material,
        })
    }
}
```

Note the `half_b` trick: using $b/2$ everywhere eliminates a factor of 2 from the quadratic formula and keeps the math slightly cleaner.

## Normal Visualization

Before adding real lighting, mapping surface normals to colors is a quick way to verify that intersections are correct. Normals are unit vectors in $[-1, 1]^3$, so we remap them to $[0, 1]^3$ for display:

```rust
fn ray_color(ray: &Ray, world: &HittableList) -> Vec3 {
    if let Some(hit) = world.hit(ray, 0.001, f32::INFINITY) {
        // Remap normal from [-1,1] to [0,1]
        return 0.5 * (hit.normal + Vec3::ONE);
    }

    // Background gradient
    let t = 0.5 * (ray.direction.y + 1.0);
    Vec3::lerp(Vec3::new(1.0, 1.0, 1.0), Vec3::new(0.5, 0.7, 1.0), t)
}
```

The result: a sphere with a smoothly varying color that corresponds to the outward normal direction. Red = +X, green = +Y, blue = +Z. It is immediately obvious if normals are flipped or the sphere center is wrong.

## What is Next

In the next part we add the camera model and implement the first Lambertian (diffuse) material using Monte Carlo sampling.
