# Research: Immich - Self-Hosted Google Photos Alternative

**Topic:** Complete guide to setting up Immich for privacy-focused photo management
**Target Audience:** Homelab enthusiasts, privacy-conscious users, families looking for Google Photos alternatives
**Date:** 2026-02-25

---

## Why Immich? (The Hook)

### Key Selling Points
- **Privacy-First:** All photos stay on YOUR hardware - no cloud provider access
- **Google Photos-like Interface:** Familiar UI makes it accessible for non-technical family members
- **Free & Open Source:** No subscription fees, unlimited storage (limited only by your hardware)
- **Mobile Apps:** iOS and Android apps with automatic backup
- **AI Features:** Face recognition, smart search, duplicate detection - all running locally

### 2026 Context
- Ranked as #1 self-hosted photo management tool in multiple 2026 comparisons
- 87,000+ GitHub stars (up from 55,000 in 2025)
- Active development: v2.0 released October 2025 with major rewrites
- Growing community: 35,000+ Discord members, 42,000+ Reddit members

---

## Installation Requirements

### Minimum Hardware
- 6GB RAM minimum
- 2 CPU cores
- Docker & Docker Compose
- Storage space for photo library

### Recommended for ML Features
- NVIDIA GPU (compute capability 5.2+) for hardware-accelerated face recognition
- Can run on CPU-only systems (slower ML processing)
- ARM devices supported (Raspberry Pi, Rockchip, etc.)

---

## Docker Compose Setup (Quick Start)

### Step 1: Create Directory
```bash
mkdir ./immich-app
cd ./immich-app
```

### Step 2: Download Config Files
```bash
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
wget -O .env https://github.com/immich-app/immich/releases/latest/download/example.env
```

### Step 3: Configure Environment Variables
Key settings in `.env`:
```env
# Where photos are stored
UPLOAD_LOCATION=./library

# Database location
DB_DATA_LOCATION=./postgres

# Set timezone
TZ=America/New_York

# Immich version (v2 is current stable)
IMMICH_VERSION=v2

# Database password (change this!)
DB_PASSWORD=your-secure-password
```

### Step 4: Start Container
```bash
docker compose up -d
```

### Step 5: Access Web UI
- Navigate to `http://<server-ip>:2283`
- First user to register becomes the admin

---

## Mobile App Setup

### Download Locations
- Google Play Store
- Apple App Store
- F-Droid
- GitHub Releases (APK)
- Obtainium (direct from source)

### Key Features
- Automatic background backup over Wi-Fi
- Selective album backup
- Direct server sync
- Same UI experience as Google Photos

---

## Machine Learning Features

### Face Recognition
- Automatically detects and groups faces
- Manual tagging support
- Can create "People" albums
- Occasional false positives (detects faces in objects)

### Smart Search
- Text-based search ("beach", "sunset", "dog")
- Uses CLIP model for semantic understanding
- GPU acceleration available for faster searches

### Duplicate Detection
- Identifies similar-looking images
- Asks for approval before deleting
- User maintains control

### Hardware Acceleration Options
- **CUDA:** NVIDIA GPUs (compute capability 5.2+)
- **ROCm:** AMD GPUs
- **OpenVINO:** Intel GPUs (Iris Xe, Arc)
- **ARM NN:** Mali GPUs
- **RKNN:** Rockchip SoCs (RK3566, RK3568, RK3576, RK3588)

---

## Feature Comparison: Immich vs Google Photos

| Feature | Immich | Google Photos |
|---------|--------|---------------|
| Storage Cost | Your hardware | 15GB free, then paid |
| Privacy | 100% local | Google has access |
| Face Recognition | ✅ Local | ✅ Cloud |
| Smart Search | ✅ Local | ✅ Cloud |
| Mobile Backup | ✅ | ✅ |
| Memories Feature | ✅ | ✅ |
| Album Sharing | ✅ Custom URLs | ✅ |
| HDR Video | ✅ | ✅ |
| Image Editor | ❌ (roadmap) | ✅ |
| Price | Free | Free tier + paid |

---

## 2025 Major Updates (Context for 2026)

### v2.0 Stable Release (October 2025)
- Complete database modernization
- New streaming sync infrastructure
- Mobile app rewrite from ground up
- Background sync without freezing

### New Features Added in 2025
- HDR video support with native player
- Search by tags and descriptions
- Manual face tagging
- Folder view in mobile app
- QR codes for shared links
- Persistent memories
- OCR (Optical Character Recognition)
- Google Cast support
- Private/locked photos
- "View similar photos" discovery
- Multiple admin accounts

---

## Platform Availability

Immich runs on:
- Docker (recommended)
- TrueNAS (built-in container app)
- Unraid
- Proxmox
- CasaOS
- Cosmos Cloud
- Runtipi
- Kubernetes

---

## External Libraries & Migration

### Importing Existing Photos
- External library support for pre-existing archives
- `immich-go` tool for Google Takeout imports
- CLI for bulk uploads
- Metadata preservation

---

## What's Coming in 2026

### Roadmap Features
- Built-in image editor (most requested!)
- Workflows
- Database restore from web UI
- Integrity check tools

---

## Backup Strategy

### Important Notes
- Database contains metadata only
- **You must manually backup UPLOAD_LOCATION**
- Recommended: Sync to remote storage
- Database has built-in backup feature

---

## Sources

1. Immich Official Documentation - https://docs.immich.app/
2. Immich 2025 Year in Review - https://immich.app/blog/2025-year-in-review
3. XDA Developers Review (Jan 2026) - "Immich is the first self-hosted Google Photos alternative my family actually uses"
4. Reddit r/homelab - 2026 homelab goals discussions
5. Medium - "5 Best Self-Hosted Tools for 2026"
6. Immich Hardware Acceleration Docs - https://docs.immich.app/features/ml-hardware-acceleration

---

## Article Outline Suggestion

1. **Introduction** - Why switch from Google Photos?
2. **What is Immich?** - Overview and key features
3. **Hardware Requirements** - What you need to run it
4. **Installation Guide** - Step-by-step Docker setup
5. **Mobile App Setup** - Automatic backup configuration
6. **ML Features Deep Dive** - Face recognition, smart search
7. **Hardware Acceleration** - GPU options for better performance
8. **Migration from Google Photos** - Using immich-go
9. **Backup Strategy** - Protecting your precious memories
10. **What's Next** - 2026 roadmap features

---

## Key Stats for Article

- 87,000+ GitHub stars
- 1,700+ contributors
- 8,800+ commits
- 35,000+ Discord members
- v2.0 stable released October 2025
- 85 new features in 2025
- 290 bug fixes in 2025

---

## Article Metadata

**Suggested Title:** "Immich: The Complete Guide to Self-Hosting Your Own Google Photos in 2026"
**Alternative Titles:**
- "Ditch Google Photos: How to Set Up Immich on Your Home Server"
- "Privacy-First Photo Management with Immich: A Complete Walkthrough"

**Suggested Tags:** homelab, self-hosted, immich, docker, privacy, photo-management, google-photos-alternative, tutorial

**Suggested Description:** Take control of your photo library with Immich - the open-source, self-hosted Google Photos alternative with AI features, mobile backup, and complete privacy.