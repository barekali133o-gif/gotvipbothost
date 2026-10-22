# GOT VIP BOT HOST

Mobile-friendly Flask starter panel with:
- Register/login (hashed passwords)
- Dashboard and per-user project list
- Upload and delete Python `.py` files (2 MB limit)
- SQLite metadata database
- Render blueprint and Gunicorn startup config

## Important
This starter **stores uploaded Python files but does not execute them**. Executing arbitrary uploaded code in the same public web service is unsafe. For real Start/Stop/24-7 hosting, add a separate isolated runner with per-bot containers, CPU/memory limits, restricted networking and secret isolation. Do not run public uploads directly with `subprocess`.

## Deploy from mobile
1. Extract ZIP and upload all files to a GitHub repository.
2. Open Render Dashboard → New → Web Service, and connect the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add `SECRET_KEY` environment variable with a long random value (Render blueprint can generate it).
6. Deploy. Try to name the service `gotvipbothost`; if taken, choose another available name.

Render free web services have ephemeral storage and may sleep when inactive. Database and uploaded files may be lost after restart/redeploy. Persistent production use needs persistent storage or a managed database/object store. Free-plan rules can change.
