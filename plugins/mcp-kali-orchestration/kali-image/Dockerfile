# MCP-Kali Docker Image
# Based on official Kali Linux rolling release with security tools pre-installed

FROM kalilinux/kali-rolling:latest

LABEL maintainer="mcp-kali"
LABEL description="Kali Linux with security tools for MCP integration"

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install base tools
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    # Core utilities
    bash \
    curl \
    wget \
    git \
    vim \
    net-tools \
    iputils-ping \
    dnsutils \
    whois \
    ca-certificates \
    # Reconnaissance tools
    nmap \
    masscan \
    dnsrecon \
    dnsenum \
    fierce \
    theharvester \
    amass \
    sublist3r \
    recon-ng \
    # Web application tools
    nikto \
    dirb \
    gobuster \
    ffuf \
    wfuzz \
    sqlmap \
    wpscan \
    whatweb \
    wafw00f \
    nuclei \
    # Exploitation tools
    metasploit-framework \
    exploitdb \
    # Password tools
    hydra \
    medusa \
    john \
    hashcat \
    hash-identifier \
    cewl \
    crunch \
    # Post-exploitation
    impacket-scripts \
    crackmapexec \
    evil-winrm \
    bloodhound \
    # Network tools
    netcat-openbsd \
    socat \
    tcpdump \
    tshark \
    responder \
    bettercap \
    # Wireless (drivers may not work in container)
    aircrack-ng \
    # Python for scripts
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for safer operations
RUN useradd -m -s /bin/bash kali && \
    echo "kali:kali" | chpasswd && \
    usermod -aG sudo kali

# Create working directories
RUN mkdir -p /opt/mcp-kali/output /opt/mcp-kali/wordlists /opt/mcp-kali/scripts

# Copy common wordlists (these are large, so we link to existing ones)
RUN ln -sf /usr/share/wordlists /opt/mcp-kali/wordlists/share

# Set working directory
WORKDIR /opt/mcp-kali

# Default to staying alive
CMD ["tail", "-f", "/dev/null"]
