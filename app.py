import os, sqlite3, secrets
from pathlib import Path
from datetime import datetime
from functools import wraps
from flask import Flask, request, redirect, url_for, render_template_string, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE = Path(__file__).resolve().parent
DATA = Path(os.getenv("DATA_DIR", str(BASE / "data")))
UPLOADS = DATA / "uploads"
DB_PATH = DATA / "panel.db"
UPLOADS.mkdir(parents=True, exist_ok=True)
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

with connect() as c:
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created TEXT NOT NULL)")
    c.execute("CREATE TABLE IF NOT EXISTS bots(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT NOT NULL, filename TEXT NOT NULL, path TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Uploaded', created TEXT NOT NULL)")

def user():
    if not session.get("uid"): return None
    with connect() as c: return c.execute("SELECT id,name,email FROM users WHERE id=?", (session["uid"],)).fetchone()

def required(fn):
    @wraps(fn)
    def wrap(*a, **kw):
        if not session.get("uid"):
            flash("Please login first.", "info")
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrap

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#080b12"><title>{{ title }} · GOT VIP BOT HOST</title><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>
:root{--bg:#080b12;--panel:#101521;--line:#252f42;--text:#f5f7fb;--muted:#8e9aaf;--purple:#9875ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -20%,#29234a 0,transparent 50%),var(--bg);color:var(--text);font:14px Inter,Arial,sans-serif;min-height:100vh}.wrap{max-width:1120px;padding:0 22px;margin:auto}.nav{height:74px;border-bottom:1px solid #ffffff0b;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;gap:10px;align-items:center;color:white;text-decoration:none;font-weight:800;letter-spacing:.5px}.logo{width:38px;height:38px;display:grid;place-items:center;border-radius:12px;background:linear-gradient(135deg,#b18cff,#5c72ff);font-size:20px}.brand b{color:#b7a0ff}.brand small{display:block;color:#8b96ab;font-size:9px;letter-spacing:2px;margin-top:3px}.nav a,.nav button{color:#b8c1d0;text-decoration:none;background:none;border:0;font:600 12px Inter;cursor:pointer;margin-left:16px}.nav .cta{background:#eee9ff;color:#211739;border-radius:8px;padding:11px 14px}.hero{text-align:center;padding:70px 0 45px}.eyebrow{color:#b5a0ff;letter-spacing:2px;font-weight:800;font-size:10px}.hero h1{font-size:clamp(45px,8vw,76px);line-height:1.05;letter-spacing:-3px;margin:23px 0 17px}.gradient{background:linear-gradient(90deg,#c4a8ff,#7894ff);color:transparent;background-clip:text}.sub{color:#9ba7bb;line-height:1.8;max-width:510px;margin:0 auto}.actions{display:flex;justify-content:center;gap:11px;margin:27px 0}.btn{display:inline-flex;justify-content:center;align-items:center;gap:20px;padding:13px 18px;border:0;border-radius:9px;text-decoration:none;font:700 12px Inter;cursor:pointer}.primary{background:linear-gradient(115deg,#a88bff,#657cff);color:white}.secondary{background:#151b29;border:1px solid #2b3548;color:#eee}.panel{border:1px solid var(--line);background:#0e1420;border-radius:14px;padding:23px;box-shadow:0 20px 60px #0003}.preview{max-width:800px;margin:38px auto 0;text-align:left}.previewtop{padding:12px 15px;border-bottom:1px solid var(--line);color:#8290a6;font-size:10px;letter-spacing:1px}.previewbody{display:grid;grid-template-columns:140px 1fr;min-height:180px}.side{padding:18px 12px;border-right:1px solid var(--line);color:#9a8bc8;font-size:11px}.side div{padding:11px;background:#292342;border-radius:7px}.mainprev{padding:20px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:15px}.stat{border:1px solid var(--line);background:#111825;border-radius:9px;padding:14px}.stat small{color:#8491a7;font-size:9px}.stat b{display:block;font-size:23px;margin-top:8px}.features{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin:26px auto;max-width:800px;text-align:left}.feature{padding:19px;border:1px solid var(--line);border-radius:12px;background:#101521}.feature h3{font-size:12px}.feature p{font-size:11px;color:#8e9aaf;line-height:1.7}.auth{max-width:420px;margin:55px auto}.auth h1{text-align:center;font-size:25px}.muted{text-align:center;color:var(--muted);font-size:12px}.form{display:grid;gap:15px;margin-top:25px}.form label{display:grid;gap:8px;color:#c8d0df;font-size:11px;font-weight:600}.form input{width:100%;background:#090e17;color:white;border:1px solid #2c364a;border-radius:9px;padding:13px;font:12px Inter;outline:none}.form input:focus{border-color:#9875ff}.full{width:100%}.note{font-size:10px;color:#c7b58e;background:#211c12;border:1px solid #4a3e2a;border-radius:8px;padding:12px;line-height:1.7;margin-top:16px}.flash{padding:12px 14px;margin-top:12px;border-radius:8px;background:#151c2a;color:#b8c6ff;border:1px solid var(--line);font-size:12px}.flash.error{color:#ffb8c0;border-color:#653943}.flash.success{color:#8be8c5;border-color:#235a48}.dash{padding:38px 0}.dashhead{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-bottom:22px}.dash h1{font-size:29px;letter-spacing:-1px;margin:12px 0 6px}.statsbar{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}.statbox{border:1px solid var(--line);background:#101521;padding:17px;border-radius:11px}.statbox small{display:block;color:#8996ab;font-size:9px;letter-spacing:1px}.statbox b{display:block;font-size:25px;margin-top:8px}.columns{display:grid;grid-template-columns:.9fr 1.1fr;gap:15px}.panel h2{font-size:15px;margin:0 0 7px}.hint{color:#8491a7;font-size:10px;line-height:1.7;margin:0 0 20px}.drop{border:1px dashed #495572;padding:20px 10px;border-radius:9px;text-align:center;background:#111725}.drop input{max-width:100%;font-size:10px}.row{display:flex;align-items:center;gap:10px;padding:13px 0;border-bottom:1px solid #222c3d}.row:last-child{border:0}.pyicon{background:#26345a;color:#a6bdff;border-radius:6px;padding:10px;font-size:10px;font-weight:800}.rowinfo{flex:1;min-width:0}.rowinfo b,.rowinfo small{display:block;overflow-wrap:anywhere}.rowinfo b{font-size:11px}.rowinfo small{font-size:9px;color:#8491a7;margin-top:5px}.badge{font-size:8px;color:#c6b5ff;background:#292343;padding:6px 8px;border-radius:20px}.delete{border:1px solid #56303a;background:#24171d;color:#ffb0bb;border-radius:6px;padding:5px 9px;cursor:pointer}.empty{text-align:center;padding:38px 8px;color:#8e9aaf;font-size:11px}.runner{margin-top:15px;padding:16px 18px;border:1px solid #38304e;background:#151426;border-radius:11px;color:#c5b5ff;font-size:11px;line-height:1.7}.footer{text-align:center;color:#667187;font-size:10px;padding:25px}.right{display:flex;align-items:center;gap:10px}.email{color:#8996ab;font-size:10px}
@media(max-width:700px){.wrap{padding:0 15px}.hero{padding-top:50px}.hero h1{letter-spacing:-2px}.features{grid-template-columns:1fr}.previewbody{grid-template-columns:100px 1fr}.side{padding:12px 6px}.mainprev{padding:12px}.stats{gap:5px}.stat{padding:9px}.stat b{font-size:17px}.columns{grid-template-columns:1fr}.dashhead{align-items:flex-start;flex-direction:column}.statsbar{gap:7px}.statbox{padding:12px 9px}.statbox small{font-size:7px;letter-spacing:.4px}.statbox b{font-size:21px}.nav{height:65px}.nav a,.nav button{margin-left:8px}.nav .cta{padding:9px}.panel{padding:17px}}@media(max-width:390px){.previewbody{grid-template-columns:1fr}.side{display:none}.statsbar{grid-template-columns:1fr}.statbox{display:flex;justify-content:space-between;align-items:center}.statbox b{margin:0}}
</style></head><body><div class="wrap"><header class="nav"><a class="brand" href="{{ url_for('index') }}"><span class="logo">G</span><span>GOT <b>VIP</b><small>BOT HOST</small></span></a><div>{% if me %}<a href="{{ url_for('dashboard') }}">Dashboard</a><form method="post" action="{{ url_for('logout') }}" style="display:inline"><button>Logout</button></form>{% else %}<a href="{{ url_for('login') }}">Login</a><a class="cta" href="{{ url_for('register') }}">Get Started ↗</a>{% endif %}</div></header>
{% for cat,msg in get_flashed_messages(with_categories=true) %}<div class="flash {{ cat }}">{{ msg }}</div>{% endfor %}
{% if page=='home' %}<section class="hero"><div class="eyebrow">● PYTHON BOT MANAGEMENT PANEL</div><h1>Your bots.<br><span class="gradient">Your control.</span></h1><p class="sub">A clean, modern dashboard to organize your Python bot projects in one place.</p><div class="actions"><a class="btn primary" href="{{ url_for('register') }}">Create free account ↗</a><a class="btn secondary" href="{{ url_for('login') }}">Sign in</a></div><div class="preview panel"><div class="previewtop">GOT VIP / CONTROL CENTER</div><div class="previewbody"><aside class="side"><div>▦ &nbsp; Overview</div><p>◈ &nbsp; My Bots</p><p>⚙ &nbsp; Settings</p></aside><div class="mainprev"><b>Dashboard overview</b><div class="stats"><div class="stat"><small>PROJECTS</small><b>—</b></div><div class="stat"><small>RUNNING</small><b>0</b></div><div class="stat"><small>ACCOUNT</small><b>✓</b></div></div></div></div></div><div class="features"><article class="feature"><h3>▦ &nbsp; Simple dashboard</h3><p>Keep your Python bot project records together in one place.</p></article><article class="feature"><h3>⬆ &nbsp; Python uploads</h3><p>Upload .py files securely and manage them from your account.</p></article><article class="feature"><h3>◈ &nbsp; Ready to extend</h3><p>Built as a starter for a future isolated bot runner.</p></article></div><div class="note"><b>Important:</b> This starter stores uploaded Python files. It does not execute user uploads until a separate secure runner is configured.</div></section>
{% elif page in ['login','register'] %}<section class="auth panel"><div class="eyebrow" style="text-align:center">{{ 'WELCOME BACK' if page=='login' else 'GET STARTED' }}</div><h1>{{ 'Sign in to your panel' if page=='login' else 'Create your account' }}</h1><p class="muted">GOT VIP BOT HOST · Python bot management</p><form class="form" method="post">{% if page=='register' %}<label>Your name<input name="name" maxlength="60" required placeholder="Your name"></label>{% endif %}<label>Email address<input name="email" type="email" required autocomplete="email" placeholder="you@example.com"></label><label>Password<input name="password" type="password" minlength="{{ 8 if page=='register' else 1 }}" required autocomplete="{{ 'new-password' if page=='register' else 'current-password' }}" placeholder="{{ 'At least 8 characters' if page=='register' else 'Your password' }}"></label><button class="btn primary full" type="submit">{{ 'Create account ↗' if page=='register' else 'Login ↗' }}</button></form><p class="muted" style="margin-top:20px">{{ 'Already registered?' if page=='register' else 'New here?' }} <a style="color:#b7a0ff" href="{{ url_for('login' if page=='register' else 'register') }}">{{ 'Login' if page=='register' else 'Create an account' }}</a></p></section>
{% elif page=='dashboard' %}<section class="dash"><div class="dashhead"><div><div class="eyebrow">● CONTROL CENTER</div><h1>Hey, {{ me['name'] }} ✦</h1><div class="email">{{ me['email'] }} · Your bot projects in one place.</div></div></div><div class="statsbar"><div class="statbox"><small>TOTAL PROJECTS</small><b>{{ total }}</b></div><div class="statbox"><small>RUNNING BOTS</small><b>0</b></div><div class="statbox"><small>UPLOAD LIMIT</small><b>2 MB</b></div></div><div class="columns"><section class="panel"><h2>Upload a bot</h2><p class="hint">Add a Python file to your project library.</p><form class="form" method="post" action="{{ url_for('upload') }}" enctype="multipart/form-data"><label>Bot project name<input name="bot_name" maxlength="80" required placeholder="My Telegram Bot"></label><label class="drop">⬆ Choose Python file<input type="file" name="bot_file" accept=".py" required><small style="display:block;color:#8491a7;margin-top:9px">Only .py files · Maximum 2 MB</small></label><button class="btn primary full" type="submit">Upload project ↗</button></form><div class="note">Files are stored only. Bot execution is not enabled in this starter.</div></section><section class="panel"><h2>My bot projects</h2><p class="hint">Your uploaded Python files · {{ total }} total</p>{% if bots %}{% for bot in bots %}<div class="row"><span class="pyicon">Py</span><div class="rowinfo"><b>{{ bot['name'] }}</b><small>{{ bot['filename'] }} · {{ bot['created'][:10] }}</small></div><span class="badge">{{ bot['status'] }}</span><form method="post" action="{{ url_for('delete', bot_id=bot['id']) }}" onsubmit="return confirm('Delete this project and its file?')"><button class="delete">×</button></form></div>{% endfor %}{% else %}<div class="empty">⌁<p>No projects yet. Upload your first .py file.</p></div>{% endif %}</section></div><div class="runner">◈ &nbsp; <b>Want to run bots 24/7?</b><br>A separate isolated runner is needed for Start / Stop, live logs and auto-restart.</div></section>{% endif %}</div><footer class="footer">GOT VIP BOT HOST · Python Bot Management Panel</footer></body></html>"""

@app.context_processor
def inject():
    return {"me": user()}

@app.route("/")
def index():
    return render_template_string(PAGE, page="home", title="Home")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name=request.form.get("name","").strip()[:60]
        email=request.form.get("email","").strip().lower()[:254]
        password=request.form.get("password","")
        if not name or not email or len(password)<8:
            flash("Name, email aur kam-se-kam 8-character password required hai.","error")
        else:
            try:
                with connect() as c:
                    cur=c.execute("INSERT INTO users(name,email,password,created) VALUES(?,?,?,?)",(name,email,generate_password_hash(password),datetime.utcnow().isoformat(timespec="seconds")))
                    session.clear(); session["uid"]=cur.lastrowid
                flash("Account create ho gaya.","success"); return redirect(url_for("dashboard"))
            except sqlite3.IntegrityError: flash("Is email se account pehle se hai.","error")
    return render_template_string(PAGE,page="register",title="Register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        with connect() as c: row=c.execute("SELECT * FROM users WHERE email=?",(request.form.get("email","").strip().lower(),)).fetchone()
        if row and check_password_hash(row["password"],request.form.get("password","")):
            session.clear(); session["uid"]=row["id"]; return redirect(url_for("dashboard"))
        flash("Email ya password sahi nahi hai.","error")
    return render_template_string(PAGE,page="login",title="Login")

@app.route("/logout",methods=["POST"])
def logout():
    session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
@required
def dashboard():
    with connect() as c:
        bots=c.execute("SELECT * FROM bots WHERE user_id=? ORDER BY id DESC",(session["uid"],)).fetchall()
    return render_template_string(PAGE,page="dashboard",title="Dashboard",bots=bots,total=len(bots))

@app.route("/bots/upload",methods=["POST"])
@required
def upload():
    name=request.form.get("bot_name","").strip()[:80]
    file=request.files.get("bot_file")
    if not name or not file or not file.filename:
        flash("Bot name aur .py file select karo.","error"); return redirect(url_for("dashboard"))
    filename=secure_filename(file.filename)
    if not filename or "." not in filename or filename.rsplit(".",1)[1].lower()!="py":
        flash("Sirf .py files allowed hain.","error"); return redirect(url_for("dashboard"))
    stored=f"{session['uid']}_{secrets.token_hex(12)}.py"; path=UPLOADS/stored; file.save(path)
    with connect() as c:
        c.execute("INSERT INTO bots(user_id,name,filename,path,status,created) VALUES(?,?,?,?,?,?)",(session["uid"],name,filename,str(path),"Uploaded",datetime.utcnow().isoformat(timespec="seconds")))
    flash("File upload ho gayi. Execution runner abhi configured nahi hai.","success")
    return redirect(url_for("dashboard"))

@app.route("/bots/<int:bot_id>/delete",methods=["POST"])
@required
def delete(bot_id):
    with connect() as c:
        row=c.execute("SELECT * FROM bots WHERE id=? AND user_id=?",(bot_id,session["uid"])).fetchone()
        if not row: abort(404)
        try:
            p=Path(row["path"]).resolve()
            if p.parent==UPLOADS.resolve() and p.exists(): p.unlink()
        except OSError: pass
        c.execute("DELETE FROM bots WHERE id=? AND user_id=?",(bot_id,session["uid"]))
    flash("Project delete kar diya.","success"); return redirect(url_for("dashboard"))

@app.errorhandler(413)
def too_big(_e):
    flash("File 2 MB se badi hai.","error"); return redirect(url_for("dashboard"))

@app.errorhandler(404)
def missing(_e):
    return "404 — Page not found",404

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")),debug=False)
