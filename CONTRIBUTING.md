# Contributing to FounderOS

Thank you for your interest in contributing to **FounderOS**! We welcome community contributions from founders, engineers, and AI researchers.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **Git**

### 2. Clone & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/your-username/FounderOS.git
cd FounderOS

# Install Frontend dependencies
npm install

# Setup Backend Virtual Environment
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Development Servers
```bash
# Terminal 1: Start React Frontend (Vite)
npm run dev

# Terminal 2: Start FastAPI Backend
cd server
uvicorn app.main:app --reload --port 8000
```
- Open `http://localhost:5173` to access the Command Center.
- API documentation is available at `http://127.0.0.1:8000/docs`.

---

## 🏛️ Architecture & Code Guidelines

Please review our technical documentation before opening a Pull Request:
- [`architecture.md`](./architecture.md): Full technical specification & database schema.
- [`harness.md`](./harness.md): Specification for C-suite agent personas and domain playbooks.

### Critical Rules
1. **Approval-Gated Execution**: Autonomous tasks must emit draft `ActionItem` objects set to status `'Ready'` awaiting founder sign-off. Never dispatch external changes automatically.
2. **Secrets & Vault**: Always encrypt API keys and OAuth tokens using `encrypt_token()` in `server/app/vault.py`. Never log plaintext secrets.
3. **No Silent Failures**: Propagate meaningful `HTTPException` detail strings from backend to frontend toast notifications.
4. **Mental Frameworks**: When adding executive lenses or debate features, ground them in real startup frameworks (YC, Reforge, Andy Grove, Peter Thiel).

---

## 🔄 Pull Request Process

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Write clean, commented code adhering to existing project conventions.
3. Test your changes locally (frontend and backend).
4. Commit your changes with descriptive commit messages:
   ```bash
   git commit -m "feat(harness): add supply chain executive lens"
   ```
5. Push to your branch and open a Pull Request against `main`.

---

## 📜 License
By contributing to FounderOS, you agree that your contributions will be licensed under the [MIT License](./LICENSE).
