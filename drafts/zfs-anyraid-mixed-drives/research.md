# ZFS AnyRaid - Research Notes

**Topic:** The Future of Mixed-Size Drive Support in ZFS  
**Research Date:** February 25, 2026  
**Article Focus:** Practical homelab applications

---

## 1. What is ZFS AnyRaid?

ZFS AnyRaid is a new VDEV (Virtual Device) type being developed for OpenZFS that fundamentally changes how ZFS handles drives of different sizes in a storage pool. It's designed to eliminate one of ZFS's biggest limitations for home server users: the requirement that all drives in a VDEV be the same size.

**Key Innovation:** AnyRaid allows users to mix and match drives of different capacities while maintaining ZFS's renowned data integrity and reliability guarantees.

**Two New Layouts:**
- **AnyRaid-Mirror** - Enhanced mirroring for mixed-drive environments
- **AnyRaid-Z1** - RAID-Z parity support for heterogeneous configurations (Phase 2)

### Why It Matters for Homelabbers

Home server users typically expand storage incrementally—adding drives over time as needs grow. Traditional ZFS layouts punish this behavior by capping all drives to the smallest disk's capacity. AnyRaid removes this penalty, making ZFS viable for users who can't afford to buy perfectly matched drive sets.

---

## 2. Current Limitations of ZFS with Mixed Drive Sizes

### The Smallest-Disk Problem

In traditional ZFS RAID-Z and mirror configurations, all drives within a VDEV operate at the size of the smallest disk. This means:

**Example:** If you have 2x3TB and 2x5TB drives in a RAID-Z1:
- Traditional ZFS treats this as 4x3TB drives
- You lose 4TB of usable capacity (the extra space on the 5TB drives)
- Upgrading one 3TB to 5TB doesn't help—you're still capped at 3TB

### Upgrade Inefficiency

The current design requires users to:
1. Replace ALL drives in a VDEV at once for capacity upgrades
2. Or deal with significant wasted space
3. Or use workarounds that add complexity (multiple VDEVs, different pools)

**Quote from Paul Dagnelie (Klara Principal ZFS Developer):**
> "All of these VDEV technologies require that all of your disks be the same size. If you're working at enterprise scale, that's fine. But if you're running a server at home, upgrades become much more expensive and time-consuming."

### The Homelab Reality

- People upgrade storage over time
- Drives get cheaper progressively
- Old drives get repurposed
- Perfect matching is expensive and wasteful

---

## 3. How AnyRaid Solves This Problem

### The Tile-Based Architecture

AnyRaid works by breaking each physical disk into smaller, fixed-size "tiles" (approximately 64GB each). These tiles are then managed by ZFS as logical units that can be allocated across drives intelligently.

**Technical Approach:**
1. Each disk is split into 64GB chunks
2. ZFS treats each chunk as a standalone logical device
3. Data is allocated across chunks with redundancy guarantees
4. ZFS knows which chunk maps to which physical disk
5. Redundancy is maintained by mirroring chunks across different physical drives

### Example: How Tiles Work

**Configuration:** 1x6TB + 2x3TB drives
- 6TB drive = 96 partitions of 64GB each
- Each 3TB drive = 48 partitions of 64GB each
- Total logical capacity: 192 partitions
- With mirroring, each logical block gets 2 copies on different physical drives

When you add a new drive, ZFS can:
- Move some 64GB chunks to the new drive
- Maintain redundancy limits automatically
- Expand usable capacity immediately

### Key Technical Components

**Indirection Map:** A new on-disk layer that enables flexible data placement across drives of different sizes. This is critical for tracking which logical tiles map to which physical locations.

**Layout Optimization:** Intelligent algorithms maximize usable capacity with mixed drive sizes while maintaining redundancy requirements.

**Data Rebalancing:** When pools are expanded, data can be redistributed across drives to improve performance on nearly full pools.

---

## 4. Timeline for Release

### Current Status (as of February 2026)

- **Still in active development**
- Announced May 2025 by HexOS/Klara
- Presented at OpenZFS Developer Summit 2025
- No confirmed release date yet

### Development Phases

**Phase 1 (Current Focus):**
- Indirection Map implementation
- Mirror Parity support
- Layout Optimization algorithms
- VDEV Expansion capability

**Phase 2 (Future):**
- RAID-Z support (AnyRaid-Z1, Z2, Z3)
- Extended parity layouts

### Community Expectations

Historically, major ZFS features (DRAID, RAID-Z expansion) took many years from concept to integration. However, the AnyRaid development pace has surprised observers:

**Quote from Jon Panozzo (HexOS CEO):**
> "The sheer speed at which AnyRaid is being developed has blown away our expectations."

---

## 5. HexOS Sponsorship and Klara Systems Involvement

### The Partnership

**HexOS (Eshtek):**
- Modern home-server OS built on TrueNAS
- Mission: Make ZFS accessible for everyday users
- Founded: 2024 by Jon Panozzo
- Sponsored AnyRaid development due to community demand

**Klara Systems:**
- Lead developer of AnyRaid
- Deep ZFS internals expertise
- Open-source filesystem engineering specialists

### Key Team Members

- **Allan Jude** - Project lead and ZFS expert
- **Paul Dagnelie** - Principal ZFS developer at Klara, AnyRaid lead
- **Igor Ostapenko** - Key implementation contributor

### Why HexOS Sponsored This

Mixed-drive support was one of the most-requested features from HexOS users. The company invested "a substantial chunk of capital" to solve a problem that directly impacted their target audience.

**Quote from Jon Panozzo:**
> "People don't buy perfectly matched drive sets. They upgrade over time, and ZFS historically punished them for that."

---

## 6. Benefits for NAS Builders

### Capacity Gains

**Example Configuration:** 1x4TB, 2x6TB, 1x8TB drives

| Layout | Usable Space | vs Traditional |
|--------|-------------|----------------|
| Traditional Mirror | 10TB | baseline |
| AnyRaid-Mirror | 12TB | +20% |
| Traditional RAID-Z1 | 12TB | baseline |
| AnyRaid-RAID-Z1 | 16TB | +33% |

### Incremental Upgrades

- Add larger drives over time
- Benefit from additional capacity immediately
- No need to replace entire VDEVs at once
- Lower upfront costs for new NAS builders

### Real Financial Impact

**Traditional approach:** Buy 4x8TB drives now ($400-600)  
**AnyRaid approach:** Start with mixed drives you have, upgrade gradually

### Reliability Preserved

- ZFS data integrity guarantees maintained
- Support for mirror parity, RAID-Z parity
- Standard resilver mechanisms work
- Data fully reconstructible after device loss

**Quote from Paul Dagnelie:**
> "This allows us to preserve the same reliability guarantees that mirrors and RAID-Z provide. If you lose a device, you can still reconstruct all of your data."

---

## 7. Comparison to Traditional RAID Setups

### vs Traditional ZFS Mirror

| Aspect | Traditional Mirror | AnyRaid-Mirror |
|--------|-------------------|----------------|
| Mixed drives | Wasted capacity | Full utilization |
| Expansion | Replace all drives | Add any drive |
| Complexity | Simple | Moderate (auto-managed) |
| Reliability | 2-copy redundancy | Same guarantees |

### vs Traditional RAID-Z

| Aspect | Traditional RAID-Z | AnyRaid-Z |
|--------|-------------------|-----------|
| Mixed drives | Capped to smallest | Full utilization |
| Upgrade path | Replace entire VDEV | Incremental expansion |
| Parity | 1-3 disk tolerance | Same tolerance |
| Capacity efficiency | Poor with mixed sizes | 20-33% better |

### vs Unraid (Popular Homelab Alternative)

**Unraid Advantages Today:**
- Native mixed-drive support
- Simple expansion
- Individual drive spin-down

**AnyRaid Advantages:**
- ZFS reliability and data integrity
- Snapshots and replication
- Native compression and dedup
- Enterprise-grade features

**Impact:** AnyRaid could make ZFS a viable alternative to Unraid for homelab users who want mixed-drive flexibility without sacrificing ZFS benefits.

---

## 8. Real-World Use Cases

### Use Case 1: The Gradual Builder

**Scenario:** Building a NAS with a $200 budget, adding drives yearly

- Year 1: Start with 2x4TB drives you already have
- Year 2: Add a 6TB drive when on sale
- Year 3: Add an 8TB drive
- Year 4: Replace failing 4TB with 10TB

**With Traditional ZFS:** Wasted capacity every step  
**With AnyRaid:** Each upgrade adds usable space immediately

### Use Case 2: The Repurposer

**Scenario:** Collecting old drives from family/friends

- Mix of 2TB, 3TB, 4TB drives from old PCs
- Can't afford new matched drives
- Want ZFS reliability for family photos

**With Traditional ZFS:** Capped to 2TB per drive  
**With AnyRaid:** Nearly full capacity utilization

### Use Case 3: The Budget Conscious

**Scenario:** Watching for deals, buying whatever's cheapest

- Buy drives when on sale, not matched sets
- Mix WD, Seagate, Toshiba
- Mix CMR and SMR (with understanding of limitations)

**With AnyRaid:** Flexibility to build over time without penalty

### Use Case 4: The Media Hoarder

**Scenario:** Massive media collection, expanding storage needs

- Start with 20TB across mixed drives
- Add drives as library grows
- Want ZFS snapshots for accidental deletion protection

**With AnyRaid:** Scale storage capacity as needed without rebuilding

---

## Key Sources

1. **XDA Developers Article** (June 2025): Overview and practical explanation
   - https://www.xda-developers.com/zfs-anyraid-will-make-it-easier-than-ever-to-build-your-first-nas/

2. **Klara Systems ZFS Roadmap**: Technical details and future plans
   - https://klarasystems.com/articles/zfs-new-features-roadmap-innovations/

3. **HexOS Official Announcement** (May 2025): Sponsorship details and phases
   - https://docs.hexos.com/blog/2025-05-22.html

4. **Klara Case Study**: Detailed technical and business context
   - https://klarasystems.com/content/https-klarasystems-com-content-case-study-hexos-zfs-mixed-drive-storage-with-anyraid/

5. **OpenZFS Developer Summit 2025**: Technical presentation by Paul Dagnelie
   - https://www.youtube.com/watch?v=zdIGhDiZWU4

6. **Reddit r/selfhosted Discussion**: Community reaction and LLM summary of technical talk
   - https://www.reddit.com/r/selfhosted/comments/1q6b8cb/zfs_anyraid_vdevs_mixandmatch_disk_sizes_in_zfs/

---

## Notable Quotes

> "This unlocks something users have wanted for years."
> — Jon Panozzo, CEO and Co-Founder of HexOS

> "With this architecture, it's very easy to add new drives and have that space immediately available—without rewriting how data is laid out."
> — Paul Dagnelie, Principal ZFS Developer, Klara Inc.

> "Klara gave us the blueprint we needed. We didn't know what we didn't know."
> — Jon Panozzo, HexOS CEO

---

## Summary for Article

**The Headline:** ZFS AnyRaid is bringing mixed-drive support to ZFS, eliminating one of the biggest pain points for home server builders. Sponsored by HexOS and developed by Klara Systems, this feature will allow ZFS users to mix drives of different sizes while maintaining ZFS's legendary data integrity—and gain 20-33% more usable capacity in the process.

**Why It Matters:** For years, homelabbers have had to choose between ZFS reliability and Unraid-style flexibility. AnyRaid removes that choice, bringing the best of both worlds to the ZFS ecosystem.

**Availability:** Still in development as of early 2026, but development is progressing faster than typical ZFS feature timelines.

---

*Research compiled for article on ZFS AnyRaid and mixed-size drive support*