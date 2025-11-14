# Quick Start

## Prerequisites
- Python 3.8+
- Virtual environment activated
- Dependencies installed: `pip install -r requirements-venv.txt`

---

## Setup

### 1. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

## Same Network Setup

### Server Instructions
```bash
python server.py --rounds 5 --min-clients 2
```
Wait for: `"Server is starting and waiting for 2 clients..."`

### Client Instructions
```bash
# Client 0
python client.py --client-id 0 --server-address 127.0.0.1:8080

# Client 1 (new terminal)
python client.py --client-id 1 --server-address 127.0.0.1:8080
```

### Dashboard (Optional)
```bash
streamlit run dashboard/app.py
```
Opens at `http://localhost:8501`

---

## Different Networks Setup

### Server Instructions
1. Find server IP:
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

2. Start server:
```bash
python server.py --rounds 5 --min-clients 2
```

### Client Instructions
Use server's IP address:
```bash
python client.py --client-id 0 --server-address <SERVER_IP>:8080
```

---

## ZeroTier Setup (Cross-Network)

### 1. Install ZeroTier
- **Windows**: Download from https://www.zerotier.com/download/
- **Mac**: `brew install --cask zerotier-one`
- **Linux**: `curl -s https://install.zerotier.com | sudo bash`

### 2. Create Network
1. Go to https://my.zerotier.com/
2. Sign up (free)
3. Create network → Copy Network ID

### 3. Join Network (All Devices)
```bash
# Windows (ZeroTier GUI)
Right-click tray icon → Join Network → Enter Network ID

# Mac/Linux
sudo zerotier-cli join <NETWORK_ID>
```

### 4. Authorize Devices
Go to https://my.zerotier.com/ → Check box to authorize each device

### 5. Get ZeroTier IPs
```bash
zerotier-cli listnetworks
```
Look for "Managed IP" (e.g., `10.147.17.5`)

### 6. Use ZeroTier IPs
```bash
# Server (no change needed)
python server.py --rounds 5 --min-clients 2

# Clients (use ZeroTier IP)
python client.py --client-id 0 --server-address 10.147.17.5:8080
```

---

## Troubleshooting

**Connection Failed**
- Check firewall allows port 8080
- Verify same network or ZeroTier IPs
- Ping test: `ping <SERVER_IP>`

**Port Already in Use**
```bash
# Kill existing process
taskkill /F /IM python.exe     # Windows
pkill python                   # Mac/Linux
```

**Dependencies Missing**
```bash
pip install -r requirements-venv.txt
```

---

## Expected Runtime
- **5 rounds** × **2-3 min/round** = **10-15 minutes**
- Training loss should decrease over rounds
