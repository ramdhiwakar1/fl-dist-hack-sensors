# ZeroTier Setup for Distributed Suppliers

## When to Use This

Use ZeroTier when your suppliers are on **different networks**:
- Different WiFi networks
- Different buildings/cities
- Home networks vs office networks
- Any scenario where direct IP connection isn't possible

## Quick Setup (5 minutes)

### Step 1: Install ZeroTier (All Machines)

**Windows:**
1. Download: https://download.zerotier.com/dist/ZeroTier%20One.msi
2. Run installer
3. ZeroTier icon appears in system tray

**Mac:**
```bash
brew install --cask zerotier-one
```

**Linux:**
```bash
curl -s https://install.zerotier.com | sudo bash
```

### Step 2: Create Network (Manufacturer Only)

1. Go to: https://my.zerotier.com/
2. Sign up (free account)
3. Click "Create A Network"
4. Copy your **16-character Network ID** (looks like: `a09acf0233xxxxxx`)

### Step 3: Join Network (All Machines)

**On each machine** (Manufacturer + All Suppliers):

**Windows:**
- Right-click ZeroTier icon in system tray
- Click "Join Network"
- Paste Network ID
- Click "Join"

**Mac/Linux:**
```bash
sudo zerotier-cli join <NETWORK_ID>
```

### Step 4: Authorize Devices (Manufacturer)

1. Go back to https://my.zerotier.com/
2. Click on your network
3. Scroll to "Members" section
4. Check the box to authorize each device

### Step 5: Get Your IPs

**On each machine:**

**Windows:**
```bash
# In PowerShell
zerotier-cli listnetworks
```

**Mac/Linux:**
```bash
zerotier-cli listnetworks
```

Look for the "Managed IP" - this is your ZeroTier IP (usually starts with `10.` or `172.`)

## Using ZeroTier IPs

### Manufacturer (Server):
```bash
# Just start normally - listens on all interfaces
python server.py --rounds 5 --min-clients 2
```

### Suppliers (Clients):
```bash
# Use the manufacturer's ZeroTier IP
python client.py --client-id 0 --server-address 10.147.17.5:8080
```

Replace `10.147.17.5` with the actual ZeroTier IP from Step 5.

## Verification

Test the connection:
```bash
# From supplier machine
ping <MANUFACTURER_ZEROTIER_IP>
```

If ping works, federated learning will work!

## Troubleshooting

**"Can't connect":**
- Check all devices are authorized in ZeroTier Central
- Verify you're using ZeroTier IPs, not regular IPs
- Check firewall isn't blocking port 8080

**"No IP assigned":**
- Wait 30 seconds after joining
- Check authorization in ZeroTier Central
- Try leaving and rejoining: `zerotier-cli leave <NETWORK_ID>`

## Security Note

- ZeroTier traffic is encrypted by default
- Only authorized devices can join your network
- You control who has access via ZeroTier Central

## That's It!

Your supplier network is now ready for federated learning across any network! 🚀

