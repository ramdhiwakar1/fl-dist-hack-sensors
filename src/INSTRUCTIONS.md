# Instructions

## Run Server
```bash
python src/server.py --rounds 5 --min-clients 2
```

## Run Client
```bash
python src/client.py --client-id 0 --server-address 127.0.0.1:8080
```

## Run Dashboard (Optional)
```bash
streamlit run dashboard/app.py
```

## Different Networks
Replace `127.0.0.1` with server IP address.

## Dependencies
```bash
pip install -r requirements-venv.txt
```

