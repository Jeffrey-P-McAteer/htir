# Meili: the Highly-Typed Information Registry (HTIR)

## Name Etymology

```
Meili is one of the Æsir in Norse mythology.
His name appears to mean "mile-stepper", and if accurate,
could mean that he was a Norse god of travel.
Given the importance of travel in Norse culture,
Meili would then have been an important figure in the Norse pantheon,
but no first-hand accounts of his status are known to exist,
so his rank and function among the Æsir remains a point of conjecture.
```
(https://mythology.wikia.org/wiki/Meili)

## Project

This repository holds

 - A library which abstracts read/write/change details about local and remote highly-typed information (sql schemas & tables are used to normalize all data, as well as some remote protocols for verifying some local data matches an expected shared schema)
 - A HITR server implementation
 - A (cli & gui) client implementation which can
    - Query an arbitrary HITR server(s) for tables
      - Tables are defined using the config file and by dynamically querying federated peers
    - Query an arbitrary table for data
    - Write arbitrary rows to a table
    - Given a server(s) & table & a condition, poll until condition is met (with possible server-side assistance via websocket)

The goal is to do what the world tried to do with http/html but better:
lower-latency protocols, encryption everywhere, machine-processable data by default,
and federation baked in (aka "I'm querying the server hitr.example.edu but if that server is part of a network return values from those servers as well").

Expect to see 1mil packets per minute between a laptop & cellphone on consumer-grade networks.

A long-term plan is to shift how organizations publish, manipulate, and trust public data:
 
  - everything is machine-processable by default
  - servers are federated by default
  - connections are p2p authenticated
  - by default data will get dropped after 3 months (ephemeral by design)

the world gains several capabilities that even large search providers today can't target:

 - scammers can't profit by tricking human eyes (Cyrillic "е" (codepoint `1077`) `еxample.org` vs ASCII number `101` "e" `example.org`)
    - They'd have to trick the human's SQL query, which the user has much greater precision and control over compared to a "keywordA keywordB keywordC" vector search with popularity metric sauce mixed in.
 - scammers can't immediately DMCA-bot legitimate content out of the air without phoning hundreds of federated organizations and talking to a human (fixes the youtube problem)
 - legitimate DMCA requests can still to go to the owner of the public key responsible for publishing the data, which server owners will have on file. All data is vaccumed after 3 months, which supports DMCA stakeholders by doing what they want by default.
 - Search becomes structured. You begin by knowing what kind of content you're looking for (names of actors, javadoc method names + description text, company phone numbers), then you (or a small UI between you and the server) construct a detailed query for the information. Gone are the days of having a search query misinterpreted or not being able to filter the entire web using a regular expression to find exactly where an oracle developer typed `;!(` in their source code.
 - Data becomes structured. The library makes it simple for two remote systems to agree on a compatible schema to pass information around, removing schema change requirements from mid-to-large scale projects. (TODO expand w/ examples, highlight future-proof details)
 - Federated sources of data mean:
    - 1) anyone can publish data, but
    - 2) if nobody finds it useful it will not propogate to many servers in the network
 - ... which solves a _ton_ of spam issues while not restricting end-user freedom
 - Also federated designs are infinitely scaleable on the cheapest of budgets.
 - Dropping data by default makes long-term storage ownership simple; if it's worth keeping around, re-publish it every 3 months!
 - ^ related to the above: for new data publishing systems, there's no need to wrestle presentaton formats: publish close-to-raw data and let clients render it however is appropriate. If you really want to be married to a font, publish a `.pdf` file.
- ^ related to the above: zero 3rd-party client-side code execution means the largest class of information system vulnerabilities is neutered from the design phase.


Benefits which _could_ be designed in but are explicitly _not_:

 - Secrecy. Yes, queries are encrypted. Yes, result sets are encrypted. No, your public key + query size will not be hidden from intermediate parties (ISPs & nosy roomates). It's too much of a design cost for too little benefit, if you want that level of secrecy go route HTIR TCP traffic through some TOR nodes until you're happy. All HTIR plans to guarantee is that the _contents_ of your query and the _contents_ of the results will be known to only you and the server(s) you query. Timing attacks and basic network analysis will still let any university know you're searching for \~900 megabytes of _somethings_ at 3am.



# Goals

 - [X] Async by default (try to use all HW cores available in server, single-thread in client)
 - [X] Use libucl for server & client configuration: https://docs.rs/libucl/latest/libucl/
 - [X] Client GUIs for windows, macos, linux, and the BSDs
 - [ ] Client -> Server comms
 - [ ] Server -> DB queries
 - [ ] Server -> shared library function call w/ some configurable caching
 - [ ] Server -> Server federation
 - [ ] Client -> local app integrations so the DB layer can be used to pass execution state around machines within the same trust


# Design

## Server

 - read system-wide `/etc/htir.toml` file
 - read per-user `$XDG_CONFIG_HOME/htir.toml` file (where if unset `$XDG_CONFIG_HOME` defaults to `$HOME/.config`)
 - Bind to `::/0` (or config IP addr) UDP port `9315`, TCP port `9315`, and unix socket `/tmp/htir.$N.sock` where `$N` is the PID of the server.
 - for UDP:
    - Incoming connections should be unencrypted CBOR data containing either:
        - Presentation of client's public key, signed timestamp, and data required to derive a shared symmetric key
        - Client public key and symmetrically encrypted Query Payload
            - Servers should remember the last 3 keys used by a public key over the last 24 hours and make an attempt to decrypt with all known keys before returning a plaintext decryption error to the client.
    - If incoming connections do not meet those requirements, return a plaintext error message pointing to the issue (bad format, unknown decryption key, error decrypting query)
 - for TCP:
    - Incoming connections may be one of:
        - TLS-encrypted HTTP session (just v1 for now, v2 sometime, and v3 is not in scope ever. All we need are websockets for the JS crowd.)
        - P2P encrypted (same schema as UDP) CBOR packet session (identical to UDP, plus control messages to ask servers to keep connections open for N seconds (defaulting to `12s`))
        - Plaintext HTTP session, which must be immediately upgraded to HTTPS
 - for unix socket:
    - No authentication planned for now (use your filesystem ownership/group perms like big boys)
    - CBOR packet streams similar to the UDP & TCP plans

 - For each incoming authenticated rate-limit-honoring CBOR Query Packet:
    - read pre-prepared SQL clause (eg `SELECT title FROM books WHERE author = :some_name`)
    - read a dictionary of query arguments (`:some_name` -> `"Joe Schmoe"` in the above example; but any basic CBOR datatype (float, int, string) will be supported) & bind them to the query
    - `// TODO`


## Client

`// TODO`

# Dependency One-Liners

Windows (using the (Chocolatey)[https://chocolatey.org/] package manager):

```bash
choco install -y imagemagick pov-ray rust python3 mingw
# For any missing binaries you will also need to add
# the directories where they were installed to
# to your PATH under Start > Edit Your Account Environment Variables > PATH
# You will also need the MSVC C/C++ redistributables available at https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019
```

MacOS (using the (Homebrew)[https://brew.sh/] package manager):

```bash
brew install povray imagemagick rust python3
```

Arch Linux:

```bash
yay -Syu povray imagemagick rust python

# Optional thing: macos cross compilation:
#  > manually setup https://github.com/tpoechtrager/osxcross
yay -Syu hfsprogs
rustup target add x86_64-apple-darwin

# Optional thing: windows cross compilation:
yay -Syu mingw-w64
rustup target add x86_64-pc-windows-gnu
```

TODO document quick setups for the crummier OSes and Gentoo.


# Build Steps

The following builds windows `.exe` files on a windows host, macos mach-o and `.app` files on macos, and all 3 on a linux host with `osxcross` and `mingw` installed.

```bash
python -m btool
```

Other btool utilities:

```bash
# Run unit tests & open browser to show un-tested lines of code
python -m btool.coverage

# Run a continuous build, executing the arguments as a command after new builds.
# Great for tweaking constants!
python -m btool.testcmd ./target/x86_64-unknown-linux-gnu/release/meili-server

# Compile & upload release to github (requires github credentials)
python -m btool.release

# Generate graphics from ditaa MFCD (requires ditaa installed)
python -m btool.gen_mfcd


```

# Examples

## Example Config

```ucl



```

# Misc

## GUI support

 - `cfg(target_os = "windows")`
    - we will use win32 bindings (from the `winapi` and `winsafe` crates) to provide graphics (win32 ships on all windows OSes)
 - `cfg(target_os = "macos")`
    - we will use Cocoa bindings (from the `cacao` crate) to provide graphics (Cocoa ships on all macos OSes)
 - `cfg(any(target_os = "linux", target_os = "freebsd", target_os = "openbsd", target_os = "netbsd"))`
    - we will use gtk4 to provide graphics; this means development and client machines need `gtk4` installed and available.


## Research

 - https://wapl.es/rust/2019/02/17/rust-cross-compile-linux-to-macos.html
 - https://github.com/phracker/MacOSX-SDKs/releases
 - https://stackoverflow.com/questions/31492799/cross-compile-a-rust-application-from-linux-to-windows


## One-liner zoo

```bash

python -m btool.release

python -m btool.testcmd ./target/x86_64-unknown-linux-gnu/release/meili-server

python -m btool.testcmd ./target/x86_64-unknown-linux-gnu/release/meili-client


```
