+++
title = 'Typestate Pattern in Rust'
date = 2024-03-01
draft = false
tags = ['rust', 'types', 'design-patterns']
description = 'Using phantom types to encode state transitions in the type system, making invalid states unrepresentable.'
+++

The typestate pattern encodes an object's valid state transitions directly in its type. The compiler then rejects code that calls a method in the wrong state — at zero runtime cost.

## The Problem

Consider a TCP connection. You should not be able to call `send()` on an unconnected socket, or `accept()` on a client connection. With a runtime enum for state, these mistakes become panics or errors at runtime. With typestate, they become compile errors.

## Phantom Types

The trick is a marker type parameter that carries state information without storing any data:

```rust
use std::marker::PhantomData;

// State marker types — zero-sized, never instantiated
pub struct Disconnected;
pub struct Connected;
pub struct Listening;

pub struct TcpSocket<State> {
    fd: RawFd,
    _state: PhantomData<State>,
}
```

`PhantomData<State>` has zero size. It only exists to make the compiler track `State` as a type parameter.

## State Transitions as Methods

Methods are defined on specific states, and return a different state:

```rust
impl TcpSocket<Disconnected> {
    pub fn new() -> Self {
        TcpSocket { fd: create_socket(), _state: PhantomData }
    }

    pub fn connect(self, addr: SocketAddr) -> Result<TcpSocket<Connected>, IoError> {
        syscall_connect(self.fd, addr)?;
        Ok(TcpSocket { fd: self.fd, _state: PhantomData })
    }

    pub fn bind(self, addr: SocketAddr) -> Result<TcpSocket<Listening>, IoError> {
        syscall_bind(self.fd, addr)?;
        syscall_listen(self.fd)?;
        Ok(TcpSocket { fd: self.fd, _state: PhantomData })
    }
}

impl TcpSocket<Connected> {
    pub fn send(&mut self, data: &[u8]) -> Result<usize, IoError> {
        syscall_send(self.fd, data)
    }

    pub fn recv(&mut self, buf: &mut [u8]) -> Result<usize, IoError> {
        syscall_recv(self.fd, buf)
    }
}
```

Calling `socket.send()` on a `TcpSocket<Disconnected>` is a compile error: the method does not exist for that type. No runtime checks, no panics, no error codes for "wrong state".

## Limitations

Typestate shines for linear state machines — states that follow a clear sequence. It gets awkward when:

- States can transition back (you need to handle the moved `self`)
- You want to store sockets of different states in the same collection (requires boxing or an enum wrapper)
- The number of states is large

For those cases, a sealed trait per state combined with a blanket `Socket<S: SocketState>` bound gives more flexibility while retaining the compile-time guarantees.
