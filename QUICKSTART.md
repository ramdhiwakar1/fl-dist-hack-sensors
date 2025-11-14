# ⚡ Quick Start - 3 Minutes to Running

## Prerequisites Check
```bash
# Check Python version (need 3.8+)
python --version

# Check you're in project root
ls pyproject.toml  # Should exist
```

## 1️⃣ Setup Virtual Environment (30 seconds)

```bash
# Create venv
python -m venv venv

# Activate
venv\Scripts\activate          # Windows
# OR
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements-venv.txt
```

## 2️⃣ Terminal 1: Start Server (10 seconds)

```bash
python server.py --rounds 5 --min-clients 2
```

**Wait for:** `"Server is starting and waiting for 2 clients..."`

## 3️⃣ Terminal 2: Start Dashboard (10 seconds)

```bash
streamlit run dashboard/app.py
```

**Browser opens automatically** at `http://localhost:8501`

## 4️⃣ Terminal 3: Start Supplier A (10 seconds)

```bash
python client.py --client-id 0
```

**Watch terminal:** Loading data → Training → Sending updates

## 5️⃣ Terminal 4: Start Supplier B (10 seconds)

```bash
python client.py --client-id 1
```

## 6️⃣ Watch the Magic! (2 minutes)

**In the dashboard you'll see:**
- ✅ Progress bar moving
- ✅ Loss decreasing (model improving!)
- ✅ Both suppliers contributing
- ✅ Real-time updates

**In ~2-3 minutes:** Training complete! 🎉

---

## What Just Happened?

1. **Server** coordinated the learning
2. **2 Suppliers** trained on their local data
3. **No data** left their machines
4. **Both got** better models than training alone
5. **You watched** it happen in real-time!

---

## Next Steps

### Add More Suppliers
```bash
# Terminal 5
python client.py --client-id 2

# Terminal 6
python client.py --client-id 3
```

### Longer Training
Edit `server.py` line 94:
```python
config=ServerConfig(num_rounds=10)  # Instead of 5
```

### Different Networks
See `zerotier_setup/setup_guide.md`

---

## Troubleshooting

**"Module not found"**
```bash
# Make sure venv is activated
pip list | grep flwr  # Should show flwr 1.23.0
```

**"Data file not found"**
```bash
# Check you're in project root
ls federated_data/hybrid/client_0.csv  # Should exist
```

**"Port 8080 already in use"**
```bash
# Kill previous server
# Windows: taskkill /F /IM python.exe
# Mac/Linux: pkill python
```

**"Clients won't connect"**
```bash
# Make sure server started first
# Check server terminal shows "waiting for clients"
```

---

## Demo for Hackathon

Follow `DEMO_SCRIPT.md` for full presentation walkthrough!

---

**That's it! You're running federated learning!** 🚀

