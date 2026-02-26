# Research: Building a Mini Home Lab Rack with Proxmox

## Key Trends for 2026

1. **Smaller, More Intentional Labs** - The trend is moving away from massive racks to compact, efficient setups
2. **Container-Focused** - LXC containers preferred over VMs for efficiency
3. **Power Efficiency** - Intel N100/N200 processors are the sweet spot
4. **Mini-PCs over Traditional Servers** - Lower power, quieter, sufficient performance

## Hardware Recommendations

### Best Mini-PC Options for Proxmox 2026

| Model | CPU | RAM | Use Case | Price Range |
|-------|-----|-----|----------|-------------|
| Intel N100 Fanless | 4 cores | 8-16GB | Silent home server | $150-250 |
| Beelink EQI13 PRO | Intel i5 | 16-32GB | Robust Proxmox server | $300-500 |
| GMKtec N95 | Celeron N95 | 8GB | Budget entry point | $100-150 |
| Intel NUC 13 Pro | i5/i7 | 32-64GB | High-performance | $400-700 |

### Key Specifications to Look For
- **CPU**: Intel N100 minimum, i5-13500T for performance
- **RAM**: 16GB minimum, 32GB recommended for multiple containers
- **Storage**: NVMe SSD for Proxmox OS, additional SSD/HDD for data
- **Network**: Dual NICs preferred (one for management, one for VM traffic)
- **Cooling**: Fanless for silent operation, or quiet fans

## Proxmox Best Practices 2026

### LXC vs VM Decision Matrix

**Use LXC Containers for:**
- VPN servers (WireGuard, Tailscale)
- DNS servers (Pi-hole, AdGuard)
- Reverse proxies (Nginx Proxy Manager, Traefik)
- Docker workloads (Portainer, individual containers)
- Media servers (Plex, Jellyfin)
- File servers (Samba, NFS)

**Use VMs for:**
- TrueNAS/ZFS storage appliances
- Windows workloads
- Services requiring kernel isolation
- Workloads needing live migration

### Storage Strategy
- ZFS native on Proxmox for data integrity
- LVM-Thin for flexible container storage
- Consider TrueNAS VM with HBA passthrough for serious NAS workloads

### Network Architecture
- Separate management network
- VLANs for IoT isolation
- Consider OPNsense/pfSense as firewall VM

## Power and Cooling

### Power Consumption Reference
| Hardware | Idle Power | Load Power |
|----------|------------|------------|
| Intel N100 mini PC | 6-10W | 25-35W |
| Intel i5 mini PC | 15-25W | 65-100W |
| Traditional 1U server | 50-100W | 200-400W |

### Cooling Considerations
- Fanless = silent but limited performance
- Large slow fans = quiet with good cooling
- Mini racks with mesh fronts for airflow

## Sources

1. https://www.virtualizationhowto.com/2026/01/inside-my-mini-rack-proxmox-and-kubernetes-home-lab-for-2026/
2. https://hometechhacker.com/5-great-proxmox-small-form-factor-hardware-options/
3. https://www.xda-developers.com/built-silent-home-server-using-intel-n100-mini-pc/
4. https://community.home-assistant.io/t/from-pi-to-powerhouse-the-ultimate-2026-home-assistant-mini-pc-build/
5. https://www.reddit.com/r/Proxmox/comments/1qnqkgl/distilling_the_proxmox_docker_in_vm_vs_lxc_debate/