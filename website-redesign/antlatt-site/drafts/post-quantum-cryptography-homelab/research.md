# Post-Quantum Cryptography for Homelabs: Research Notes

**Research Date:** February 2025
**Purpose:** Blog article research for antlatt.com

---

## Executive Summary

Post-quantum cryptography (PQC) is no longer theoretical—it's production-ready and being deployed now. With NIST finalizing standards in August 2024 and OpenSSH making PQC the default in version 10.0 (April 2025), homelab enthusiasts can start implementing quantum-resistant security today. This research covers everything needed to prepare your homelab for the quantum era.

---

## The Quantum Threat: Why Act Now?

### Timeline to "Q-Day"

- **Current state (2024-2025):** Quantum computers are in the NISQ era (Noisy Intermediate-Scale Quantum), with high error rates incompatible with code-breaking
- **Expert estimates for cryptographically relevant quantum computers (CRQC):** Early-to-mid 2030s (2028-2035 range)
- **NIST timeline:** RSA and ECC expected to be phased out by 2030, completely disallowed by 2035

### The "Harvest Now, Decrypt Later" Threat

The primary immediate concern is not that quantum computers can break encryption today, but that adversaries can:
1. Intercept and store encrypted traffic today
2. Decrypt it in the future when quantum computers become capable

**Key insight:** Data with long-term confidentiality requirements (10+ years) needs PQC protection NOW.

---

## NIST Standards Finalized (2024-2025)

### FIPS 203: ML-KEM (formerly CRYSTALS-Kyber)
- **Purpose:** Key Encapsulation Mechanism (KEM) for key exchange
- **Based on:** Lattice-based cryptography
- **Use case:** Establishing shared secrets for encryption

| Parameter Set | Public Key | Secret Key | Ciphertext | Security Level |
|---------------|------------|------------|------------|----------------|
| ML-KEM-512 | 800 bytes | 1,632 bytes | 768 bytes | ~AES-128 |
| ML-KEM-768 | 1,184 bytes | 2,400 bytes | 1,088 bytes | ~AES-192 |
| ML-KEM-1024 | 1,568 bytes | 3,168 bytes | 1,568 bytes | ~AES-256 |

### FIPS 204: ML-DSA (formerly CRYSTALS-Dilithium)
- **Purpose:** Digital signatures for authentication
- **Based on:** Lattice-based cryptography
- **Use case:** Certificates, code signing, SSH keys

| Parameter Set | Public Key | Private Key | Signature Size | Security Level |
|---------------|------------|-------------|----------------|----------------|
| ML-DSA-44 | 1,312 bytes | 2,560 bytes | 2,420 bytes | ~AES-128 |
| ML-DSA-65 | 1,952 bytes | 4,032 bytes | 3,293 bytes | ~AES-192 |
| ML-DSA-87 | 2,592 bytes | 4,896 bytes | 4,595 bytes | ~AES-256 |

### FIPS 205: SLH-DSA (SPHINCS+)
- **Purpose:** Hash-based digital signatures (backup option)
- **Advantage:** Based on hash functions, well-understood security
- **Disadvantage:** Larger signature sizes
- **Use case:** Long-term signatures where size matters less

### FN-DSA (FALCON) - Expected 2025
- **Purpose:** Digital signatures
- **Advantage:** Smaller signatures than ML-DSA
- **Status:** Draft standard, finalization expected in 2025

---

## Size Comparison: PQC vs Classical

| Algorithm Type | Classical (RSA/ECC) | Post-Quantum (ML-KEM/ML-DSA) |
|----------------|---------------------|------------------------------|
| Key Exchange (public key) | 32 bytes (X25519) | 1,184 bytes (ML-KEM-768) |
| Signature | 64 bytes (Ed25519) | 3,293 bytes (ML-DSA-65) |
| RSA-2048 signature | 256 bytes | 2,420 bytes (ML-DSA-44) |

**Key takeaway:** PQC keys and signatures are larger, but still practical for most applications.

---

## SSH: OpenSSH Post-Quantum Support

### Version Timeline

| OpenSSH Version | Release | PQC Support |
|-----------------|---------|-------------|
| 9.0 | April 2022 | `sntrup761x25519-sha512` hybrid KEX (default) |
| 9.9 | Late 2024 | Added `mlkem768x25519-sha256` hybrid KEX |
| 10.0 | April 2025 | `mlkem768x25519-sha256` becomes DEFAULT |
| 10.1 | TBD | Warnings for non-PQC key exchange |

### How It Works

OpenSSH uses **hybrid key exchange**—combining classical (X25519) with post-quantum algorithms:
- Security is at least as strong as the best algorithm
- If one algorithm is broken, the other still protects
- Backward compatible with legacy systems

### Check Your Current Setup

```bash
# Check supported key exchange algorithms
ssh -Q kex | grep -E "(mlkem|sntrup)"

# Check what the server supports
sshd -T | grep kex
```

### Server Configuration (`/etc/ssh/sshd_config`)

```bash
# Prioritize post-quantum algorithms
KexAlgorithms mlkem768x25519-sha256,sntrup761x25519-sha512,curve25519-sha256

# Or append to existing defaults
KexAlgorithms +mlkem768x25519-sha256,sntrup761x25519-sha512
```

### Client Configuration (`~/.ssh/config`)

```ssh
Host *
    KexAlgorithms mlkem768x25519-sha256,sntrup761x25519-sha512,curve25519-sha256
```

### Verify Connection is Using PQC

```bash
# Verbose connection to see negotiated algorithm
ssh -v user@hostname 2>&1 | grep "kex算法\|kex algorithm"

# Output should show something like:
# debug1: kex: algorithm: mlkem768x25519-sha256
```

---

## VPN: WireGuard Post-Quantum Solutions

### The Challenge

WireGuard's key exchange is based on Curve25519, which is vulnerable to quantum attacks. The protocol itself doesn't natively support PQC yet, but solutions exist.

### Solution 1: Rosenpass (Recommended for Homelabs)

**What it is:** Open-source post-quantum key exchange protocol that layers on top of WireGuard

**How it works:**
- Uses Classic McEliece and Kyber (ML-KEM) for quantum-resistant key exchange
- Rotates WireGuard pre-shared keys (PSK) every ~2 minutes
- Provides hybrid security: WireGuard + Rosenpass

**Installation (Linux):**

```bash
# Install dependencies
sudo apt-get install libsodium-dev libclang-dev cmake pkg-config git build-essential wireguard

# Download pre-built binary (recommended)
wget https://github.com/rosenpass/rosenpass/releases/latest/download/rosenpass-x86_64-linux.tar
tar xf rosenpass-x86_64-linux.tar
sudo install bin/rosenpass /usr/local/bin
sudo install bin/rp /usr/local/bin

# Or build from source
git clone https://github.com/rosenpass/rosenpass.git
cd rosenpass
cargo build --release
sudo install target/release/rosenpass /usr/local/bin
sudo install target/release/rp /usr/local/bin
```

**Basic Setup (Server):**

```bash
# Generate Rosenpass keys
rp genkey server.rosenpass-secret
rp pubkey server.rosenpass-secret server.rosenpass-public

# Start Rosenpass-enhanced WireGuard
rp exchange server.rosenpass-secret dev rosenpass0 listen 0.0.0.0:9999 \
  peer client.rosenpass-public allowed-ips 10.0.0.0/24

# Assign IP
ip a add 10.0.0.1/24 dev rosenpass0
```

**Basic Setup (Client):**

```bash
# Generate keys
rp genkey client.rosenpass-secret
rp pubkey client.rosenpass-secret client.rosenpass-public

# Connect to server
rp exchange client.rosenpass-secret dev rosenpass0 \
  peer server.rosenpass-public endpoint SERVER_IP:9999 allowed-ips 10.0.0.0/24

# Assign IP
ip a add 10.0.0.2/24 dev rosenpass0
```

### Solution 2: NetBird (Managed Solution)

- Modern mesh VPN built on WireGuard
- Embeds Rosenpass server for PQC
- Easier management for multiple nodes
- Supports SSO and access control lists

**Installation:**

```bash
# Linux
curl -OL https://github.com/netbirdio/netbird/releases/latest/download/netbird_linux_amd64.deb
sudo dpkg -i netbird_linux_amd64.deb

# Or use the installer
curl -fsSL https://pkgs.netbird.io/install.sh | sh
```

### Solution 3: Commercial VPN Providers

| Provider | Status | Technology |
|----------|--------|------------|
| Mullvad VPN | Active, default ON | ML-KEM hybrid with WireGuard |
| ExpressVPN | Active | Post-Quantum WireGuard, Lightway protocol |
| NordVPN | Active | NordLynx (WireGuard) with PQC |
| Windscribe | Active | PQC-enhanced WireGuard |

**For homelab:** Self-hosted Rosenpass or NetBird is preferred for control.

---

## Web Servers: TLS with Post-Quantum

### Caddy 2.10+ (Easiest)

**Requirements:**
- Caddy 2.10 or later
- Built with Go 1.24+

**Configuration:** Zero config needed! X25519MLKEM768 is enabled BY DEFAULT.

```bash
# Install with xcaddy (ensures correct Go version)
xcaddy build --with github.com/caddyserver/caddy/v2@latest

# Or download pre-built
# Caddy's official downloads include Go 1.24+ builds
```

**Verify:**

```bash
# Check TLS connection
openssl s_client -connect yourdomain.com:443 -tls1_3 2>&1 | grep "Key-Exchange"

# Or use test site
curl -v https://yourdomain.com 2>&1 | grep -i "key exchange"
```

### Nginx with OpenSSL 3.5+

**Prerequisites:**
- OpenSSL 3.5+ (released April 2025)
- Nginx compiled against new OpenSSL

**Installation (Ubuntu/Debian):**

```bash
# Build OpenSSL 3.5 from source
wget https://www.openssl.org/source/openssl-3.5.0.tar.gz
tar -xzf openssl-3.5.0.tar.gz
cd openssl-3.5.0
./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl
make -j$(nproc)
sudo make install

# Build Nginx against new OpenSSL
wget http://nginx.org/download/nginx-1.27.0.tar.gz
tar -xzf nginx-1.27.0.tar.gz
cd nginx-1.27.0
./configure --with-openssl=/path/to/openssl-3.5.0 \
  --with-http_ssl_module \
  --with-openssl-opt='enable-ml-kem enable-ml-dsa'
make -j$(nproc)
sudo make install
```

**Nginx Configuration:**

```nginx
http {
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers on;
    # OpenSSL 3.5+ will negotiate ML-KEM automatically when client supports it
}
```

### Apache with OpenSSL 3.5+

Similar to Nginx—needs compilation against OpenSSL 3.5+:

```apache
<VirtualHost *:443>
    SSLEngine on
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    # PQC key exchange handled by OpenSSL
</VirtualHost>
```

### Using Open Quantum Safe (for experimentation)

For testing before OpenSSL 3.5 was available, liboqs provides a wider range of algorithms:

```bash
# Install liboqs
git clone https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -GNinja .. -DBUILD_SHARED_LIBS=ON
ninja
sudo ninja install

# Install oqsprovider for OpenSSL 3.x
git clone https://github.com/open-quantum-safe/oqs-provider.git
cd oqs-provider
mkdir build && cd build
cmake -GNinja ..
ninja
sudo ninja install

# Configure OpenSSL to load oqsprovider
# Edit /usr/local/ssl/openssl.cnf
```

```ini
[openssl_init]
providers = provider_sect

[provider_sect]
default = default_sect
oqs = oqs_sect

[oqs_sect]
activate = 1
module = /usr/local/lib/ossl-modules/oqsprovider.so
```

---

## File Encryption: Age with Post-Quantum

Age 1.3.0+ includes native post-quantum support using ML-KEM.

### Installation

```bash
# Ubuntu/Debian
sudo apt install age

# Arch Linux
sudo pacman -S age

# macOS
brew install age

# Or download binary
wget https://dl.filippo.io/age/latest?for=linux/amd64 -O age
chmod +x age
sudo mv age /usr/local/bin/
```

### Generate Post-Quantum Keys

```bash
# Generate PQ key pair
age-keygen -pq -o pq-key.txt

# Output shows public key starting with age1pq1...
# Note: PQ recipients are ~2000 characters long!
```

### Encrypt with Post-Quantum

```bash
# Encrypt a file
age -r age1pq1... -o secrets.tar.gz.age secrets.tar.gz

# Check if file uses PQ encryption
age-inspect secrets.tar.gz.age

# Output includes:
# - "mlkem768x25519"
# - "This file uses post-quantum encryption."
```

### Using age-plugin-pq (for older versions)

```bash
# Install plugin separately
go install filippo.io/age/cmd/age-plugin-pq@latest
sudo mv ~/go/bin/age-plugin-pq /usr/local/bin/

# Now any age version can use PQ
age-plugin-pq -identity > pq-identity.txt
```

---

## Certificate Authorities: Smallstep step-ca

### Current Status

- step-ca v0.28.3+ supports TLS 1.3 hybrid key exchange (X25519MLKEM768)
- Requires environment variable until Go 1.24: `GODEBUG=tlsmlkem=1`
- Full PQC certificates (hybrid X.509) still in development

### Quick Setup

```bash
# Install step-cli and step-ca
wget https://dl.smallstep.com/gh-release/gh-release/gh-release/step-cli/step-cli_linux_amd64.tar.gz
tar -xzf step-cli_linux_amd64.tar.gz
sudo mv step /usr/local/bin/

wget https://dl.smallstep.com/gh-release/gh-release/gh-release/step-ca/step-ca_linux_amd64.tar.gz
tar -xzf step-ca_linux_amd64.tar.gz
sudo mv step-ca /usr/local/bin/

# Initialize CA
step ca init --name="Homelab CA" --provisioner="admin" --dns="ca.homelab.local"

# Enable PQC
export GODEBUG=tlsmlkem=1

# Start CA
step-ca config/ca.json
```

### Generate Certificates

```bash
# Root certificate with classical algorithm (current default)
step ca create Homelab-CA homelab-ca homelab.local --ca-profile root-ca

# For future PQC certificates, watch for:
# - Hybrid certificate support
# - ML-DSA integration
# - Standardization in X.509 extensions
```

---

## OpenSSL 3.5: Native PQC Support

Released April 8, 2025, OpenSSL 3.5 is a game-changer:

### Features

- **ML-KEM (FIPS 203)**: Native support for key encapsulation
- **ML-DSA (FIPS 204)**: Native support for digital signatures  
- **SLH-DSA (FIPS 205)**: Hash-based signature support
- **QUIC**: Full server-side QUIC support
- **LTS**: Long-term support until April 2030

### Generate PQC Keys and Certificates

```bash
# Generate ML-DSA key pair
openssl genpkey -algorithm ml-dsa65 -out mldsa65_key.pem

# Create self-signed certificate
openssl req -x509 -new -key mldsa65_key.pem -out mldsa65_cert.pem -days 365 \
  -subj "/CN=homelab.local"

# Verify certificate
openssl x509 -in mldsa65_cert.pem -text -noout | grep "Signature Algorithm"
# Should show: ml-dsa65
```

### Generate ML-KEM Keys

```bash
# Generate ML-KEM-768 key pair
openssl genpkey -algorithm ml-kem-768 -out mlkem768_key.pem

# Extract public key
openssl pkey -in mlkem768_key.pem -pubout -out mlkem768_pub.pem
```

---

## Browser Support

| Browser | Version | PQC Support |
|---------|---------|-------------|
| Chrome | 116+ | `X25519Kyber768Draft00` supported, enabled by default |
| Chrome | 124+ | `X25519MLKEM768` enabled by default |
| Firefox | 125+ | `X25519MLKEM768` enabled by default |
| Edge | 116+ | Same as Chrome (Chromium-based) |
| Safari | TBD | In development |

### Verify Browser Connection

Chrome DevTools → Security tab → Connection shows:
- "TLS 1.3" 
- Key exchange should show "X25519MLKEM768" for PQ connections

---

## Cloudflare: Free PQC for Everyone

Cloudflare provides post-quantum TLS **for free** to all customers:

- Enabled March 2023
- Never charging for PQC—it's the new baseline
- By March 2025: 38% of TLS 1.3 connections use PQC
- Automatic for all proxied domains

**For homelab users with custom domains:** Point your domain through Cloudflare for automatic PQC without any server configuration.

---

## Performance Considerations

### ML-KEM vs Classical Key Exchange

| Operation | X25519 | ML-KEM-768 | Difference |
|-----------|--------|------------|------------|
| Key generation | ~30,000 cycles | ~50,000 cycles | ~1.7x slower |
| Encapsulation | ~30,000 cycles | ~65,000 cycles | ~2x slower |
| Decapsulation | ~30,000 cycles | ~50,000 cycles | ~1.7x slower |

**Reality check:** For most applications, this difference is negligible. A TLS handshake might take 1-2ms longer—imperceptible to users.

### ML-DSA vs Classical Signatures

| Operation | Ed25519 | ML-DSA-65 | Difference |
|-----------|---------|-----------|------------|
| Sign | ~50,000 cycles | ~150,000 cycles | ~3x slower |
| Verify | ~100,000 cycles | ~80,000 cycles | Actually faster |
| Signature size | 64 bytes | 3,293 bytes | 50x larger |

### Practical Impact

- **TLS handshake overhead:** Minimal (< 2ms)
- **Certificate size:** Larger certs mean more bandwidth, but still reasonable
- **SSH sessions:** No perceptible difference
- **VPN throughput:** WireGuard + Rosenpass adds minimal latency

---

## Implementation Checklist for Homelab

### Phase 1: Assessment (Week 1)

- [ ] Inventory all SSH servers and clients
- [ ] Check OpenSSH versions (`ssh -V`)
- [ ] List VPN services in use
- [ ] Identify web servers and TLS termination points
- [ ] Audit file encryption tools
- [ ] Note any certificate authorities (internal PKI)

### Phase 2: SSH Hardening (Week 2)

- [ ] Upgrade to OpenSSH 9.9+ (10.0+ preferred)
- [ ] Add PQC algorithms to `sshd_config`
- [ ] Add PQC algorithms to `~/.ssh/config`
- [ ] Test connections with `-v` to verify negotiation
- [ ] Monitor logs for compatibility issues

### Phase 3: VPN Security (Week 3)

- [ ] Evaluate WireGuard usage
- [ ] Install and configure Rosenpass for critical tunnels
- [ ] Or migrate to NetBird for managed PQC VPN
- [ ] Test failover scenarios

### Phase 4: TLS Upgrades (Week 4)

- [ ] Upgrade to OpenSSL 3.5+ or install liboqs provider
- [ ] For Caddy: upgrade to 2.10+ (automatic PQC)
- [ ] For Nginx/Apache: recompile against OpenSSL 3.5+
- [ ] Test with `openssl s_client` and browser DevTools

### Phase 5: File Encryption (Ongoing)

- [ ] Upgrade Age to 1.3.0+
- [ ] Generate post-quantum keys for new secrets
- [ ] Re-encrypt critical backups with PQ keys
- [ ] Consider key rotation strategy

---

## Recommended Tool Stack for Homelab

| Category | Recommended Tool | PQC Support | Difficulty |
|----------|------------------|-------------|------------|
| SSH | OpenSSH 10.0+ | Native (default) | Easy |
| VPN | Rosenpass + WireGuard | Yes (via PSK rotation) | Medium |
| VPN (managed) | NetBird | Yes (embedded Rosenpass) | Easy |
| Web Server | Caddy 2.10+ | Native (default) | Easy |
| Web Server | Nginx + OpenSSL 3.5 | Native | Medium |
| File Encryption | Age 1.3.0+ | Native (`-pq` flag) | Easy |
| CA/PKI | Smallstep step-ca | Hybrid TLS 1.3 | Medium |
| TLS Proxy | Cloudflare (free) | Native | Easy |

---

## Sources and References

### NIST Standards
- [NIST FIPS 203: ML-KEM](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf)
- [NIST FIPS 204: ML-DSA](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf)
- [NIST FIPS 205: SLH-DSA](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf)
- [NIST PQC Standardization Announcement (Aug 2024)](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)

### OpenSSH
- [OpenSSH Post-Quantum Documentation](https://www.openssh.org/pq.html)
- [OpenSSH 10.0 Release Notes](https://www.phoronix.com/news/OpenSSH-10.0-Released)

### VPN and Rosenpass
- [Rosenpass Official Documentation](https://rosenpass.eu/)
- [Rosenpass GitHub](https://github.com/rosenpass/rosenpass)
- [Arch Linux Rosenpass Wiki](https://wiki.archlinux.org/title/Rosenpass)
- [NetBird PQC Documentation](https://docs.netbird.io/client/post-quantum-cryptography)

### OpenSSL
- [OpenSSL 3.5 Release Announcement](https://openssl-library.org/post/2025-04-08-openssl-35-final-release/)
- [Open Quantum Safe Project](https://openquantumsafe.org/)
- [liboqs GitHub](https://github.com/open-quantum-safe/liboqs)

### Web Servers
- [Caddy Post-Quantum Discussion](https://caddy.community/t/post-quantum-caddy/30260)
- [Caddy TLS Configuration](https://caddyserver.com/docs/caddyfile/directives/tls)

### Age Encryption
- [Age GitHub Repository](https://github.com/FiloSottile/age)
- [Age Specification](https://age-encryption.org/v1)

### Certificate Authorities
- [Smallstep PQC Blog Post](https://smallstep.com/blog/post-quantum-cryptography-at-smallstep/)
- [step-ca Documentation](https://smallstep.com/docs/step-ca/)

### Cloudflare
- [Cloudflare PQC Announcement](https://www.cloudflare.com/press/press-releases/2023/cloudflare-democratizes-post-quantum-cryptography-by-delivering-it-for-free/)
- [Cloudflare PQC Research](https://pq.cloudflareresearch.com/)

### General Resources
- [IBM - NIST PQC Standards Explained](https://research.ibm.com/blog/nist-pqc-standards)
- [Cloudflare 2024 PQC Progress](https://blog.cloudflare.com/pq-2024/)
- [Red Hat RHEL 10 PKC Preview](https://www.redhat.com/en/blog/post-quantum-cryptography-red-hat-enterprise-linux-10)
- [Homelab PQC Guide](https://williamzujkowski.github.io/posts/preparing-your-homelab-for-the-quantum-future-post-quantum-cryptography-migration/)

---

## Glossary

| Term | Definition |
|------|------------|
| **CRQC** | Cryptographically Relevant Quantum Computer - a quantum computer capable of breaking current encryption |
| **FIPS** | Federal Information Processing Standards - NIST's cryptographic standards |
| **KEM** | Key Encapsulation Mechanism - a method to exchange symmetric keys |
| **Lattice-based crypto** | Cryptography based on the hardness of lattice problems, believed quantum-resistant |
| **ML-KEM** | Module-Lattice-Based Key Encapsulation Mechanism (standardized Kyber) |
| **ML-DSA** | Module-Lattice-Based Digital Signature Algorithm (standardized Dilithium) |
| **NISQ** | Noisy Intermediate-Scale Quantum - current era of quantum computers with high error rates |
| **PQC** | Post-Quantum Cryptography - algorithms resistant to quantum attacks |
| **Q-Day** | The future date when quantum computers can break current encryption |
| **SLH-DSA** | Stateless Hash-Based Digital Signature Algorithm (SPHINCS+) |

---

*Research compiled for antlatt.com blog article. Last updated: February 2025.*