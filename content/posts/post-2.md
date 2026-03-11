+++
title = 'Ergonomic Error Handling in Rust'
date = 2024-02-20
draft = false
tags = ['rust', 'design-patterns']
description = 'Practical patterns for expressing errors clearly: the ? operator, thiserror, anyhow, and when to use each.'
+++

Rust forces you to handle errors explicitly, which is good. It does not force you to write mountains of boilerplate, which is even better — once you know the right tools. The ecosystem has converged on a small set of patterns that cover almost every case cleanly.

## The ? Operator

`?` is syntactic sugar for "if this is an error, convert it and return early". It replaces the most common match pattern:

```rust
// Before
let file = match File::open(path) {
    Ok(f)  => f,
    Err(e) => return Err(e.into()),
};

// After
let file = File::open(path)?;
```

The `.into()` call is the key detail: `?` runs `From::from` on the error, which means your function's return type must implement `From<E>` for every error type `E` that appears behind a `?`. This is what drives the design of your error types.

## Library Code: thiserror

For libraries, error types must be explicit. Callers depend on matching specific variants; an opaque error type forces them to stringify and parse, which is terrible. `thiserror` derives the `Error` trait with minimal boilerplate:

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum SceneError {
    #[error("mesh file not found: {path}")]
    MeshNotFound { path: PathBuf },

    #[error("unsupported material type: {0}")]
    UnsupportedMaterial(String),

    #[error("failed to read scene file")]
    Io(#[from] std::io::Error),
}
```

The `#[from]` attribute generates a `From<io::Error>` impl automatically, so `?` on any `io::Error` inside a function returning `Result<_, SceneError>` just works. The `#[error("...")]` string becomes the `Display` impl — no manual `fmt` implementation needed.

## Application Code: anyhow

Applications care about propagating errors to the user, not about callers matching variants. `anyhow::Error` is a type-erased error that carries a backtrace and can wrap anything that implements `std::error::Error`:

```rust
use anyhow::{Context, Result};

fn load_scene(path: &Path) -> Result<Scene> {
    let text = fs::read_to_string(path)
        .with_context(|| format!("could not read scene file: {}", path.display()))?;

    let scene: Scene = toml::from_str(&text)
        .context("scene file is not valid TOML")?;

    Ok(scene)
}
```

`.context()` and `.with_context()` attach a human-readable explanation to the error without losing the underlying cause. When the error reaches `main` and is printed, the full chain is visible:

```
Error: could not read scene file: scenes/cornell.toml

Caused by:
    No such file or directory (os error 2)
```

## Choosing Between Them

The rule of thumb: use `thiserror` for anything in a library crate, use `anyhow` in binary crates and integration code. They compose cleanly — a library function returns `Result<T, MyError>`, the application function calls it with `?`, and `anyhow` wraps `MyError` transparently since it implements `std::error::Error`.

## Avoiding the Trap of String Errors

A common shortcut is returning `Result<T, String>` or `Result<T, Box<dyn Error>>`. Both lose structured information: `String` prevents callers from handling specific cases programmatically, and `Box<dyn Error>` without `anyhow` loses the error chain. If you find yourself writing either, it is almost always worth spending two minutes defining a proper enum with `thiserror` instead.
