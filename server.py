#!/usr/bin/env python3
"""
Apex Institute — Pure Python Backend Server
No external dependencies required. Uses only Python standard library.
Serves both the API (at /api/v1/) and the React frontend (from frontend/dist/).

Usage:
    python server.py

Default port: 5000
"""

import json
import os
import sys
import time
import hashlib
import hmac
import base64
import re
import uuid
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
PORT = int(os.environ.get("PORT", 5000))
JWT_SECRET = os.environ.get("JWT_SECRET", "apex_institute_secret_2026_change_me")
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "backend" / "data" / "store.json"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js":   "application/javascript",
    ".mjs":  "application/javascript",
    ".css":  "text/css",
    ".json": "application/json",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
    ".woff": "font/woff",
    ".woff2":"font/woff2",
    ".ttf":  "font/ttf",
    ".webmanifest": "application/manifest+json",
}

# ─────────────────────────────────────────
# JWT (pure Python — HS256 only)
# ─────────────────────────────────────────
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    pad = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * (pad % 4))

def jwt_sign(payload: dict, secret: str, expires_in_hours: int = 72) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = dict(payload)
    payload["iat"] = int(time.time())
    payload["exp"] = int(time.time()) + expires_in_hours * 3600
    body = _b64url_encode(json.dumps(payload).encode())
    sig_input = f"{header}.{body}".encode()
    sig = hmac.new(secret.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{body}.{_b64url_encode(sig)}"

def jwt_verify(token: str, secret: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b, body_b, sig_b = parts
        expected_sig = hmac.new(secret.encode(), f"{header_b}.{body_b}".encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_decode(sig_b), expected_sig):
            return None
        payload = json.loads(_b64url_decode(body_b))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

# ─────────────────────────────────────────
# Password hashing (SHA-256 based, bcrypt-compatible via stored hashes)
# ─────────────────────────────────────────
def hash_password(password: str) -> str:
    salt = uuid.uuid4().hex
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${h}"

def check_password(password: str, stored_hash: str) -> bool:
    # Support our sha256 format
    if stored_hash.startswith("sha256$"):
        _, salt, h = stored_hash.split("$", 2)
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    # Fallback: direct compare (for bcrypt hashes from old Node backend, treat as mismatch)
    return False

# ─────────────────────────────────────────
# Local Data Store
# ─────────────────────────────────────────
_store_lock = threading.Lock()

DEFAULT_STORE = {
    "users": [
        {
            "id": 1,
            "name": "Admin User",
            "email": "admin@apex.com",
            "phone": "+919876543210",
            "password_hash": "sha256$defaultsalt$" + hashlib.sha256(("defaultsalt" + "admin123").encode()).hexdigest(),
            "role": "ADMIN",
            "status": "active",
            "created_at": "2026-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Rahul Sharma",
            "email": "rahul@apex.com",
            "phone": "+919876543211",
            "password_hash": "sha256$teachersalt$" + hashlib.sha256(("teachersalt" + "teacher123").encode()).hexdigest(),
            "role": "TEACHER",
            "status": "active",
            "created_at": "2026-01-01T00:00:00Z"
        }
    ],
    "batches": [
        {"id": 1, "name": "Class 10 - Morning", "subject": "Maths & Science", "timing": "7:00 AM - 9:00 AM", "teacher_id": 2, "status": "active", "created_at": "2026-01-01T00:00:00Z"},
        {"id": 2, "name": "Class 11 PCM - Evening", "subject": "Physics, Chemistry, Maths", "timing": "4:00 PM - 6:00 PM", "teacher_id": 2, "status": "active", "created_at": "2026-01-01T00:00:00Z"},
        {"id": 3, "name": "Class 12 PCB - Morning", "subject": "Physics, Chemistry, Biology", "timing": "7:00 AM - 9:00 AM", "teacher_id": 2, "status": "active", "created_at": "2026-01-01T00:00:00Z"},
    ],
    "students": [
        {"id": 1, "name": "Anjali Singh", "roll_no": "10A01", "parent_name": "Ramesh Singh", "parent_phone": "+919800000001", "batch_id": 1, "address": "123 Main St, Lucknow", "student_class": "10", "stream": None, "board": "UP Board", "subject_fees": [{"subject": "Maths", "fee": 1500}, {"subject": "Science", "fee": 1500}], "total_fee": 3000, "joining_date": "2026-04-01", "status": "active", "created_at": "2026-04-01T00:00:00Z"},
        {"id": 2, "name": "Rohan Verma", "roll_no": "10A02", "parent_name": "Suresh Verma", "parent_phone": "+919800000002", "batch_id": 1, "address": "456 Park Lane, Lucknow", "student_class": "10", "stream": None, "board": "CBSE", "subject_fees": [{"subject": "Maths", "fee": 2000}, {"subject": "Science", "fee": 2000}], "total_fee": 4000, "joining_date": "2026-04-01", "status": "active", "created_at": "2026-04-01T00:00:00Z"},
        {"id": 3, "name": "Priya Gupta", "roll_no": "11B01", "parent_name": "Anil Gupta", "parent_phone": "+919800000003", "batch_id": 2, "address": "789 Civil Lines, Lucknow", "student_class": "11", "stream": "PCM", "board": "CBSE", "subject_fees": [{"subject": "Physics", "fee": 2000}, {"subject": "Chemistry", "fee": 2000}, {"subject": "Maths", "fee": 2000}], "total_fee": 6000, "joining_date": "2026-04-01", "status": "active", "created_at": "2026-04-01T00:00:00Z"},
        {"id": 4, "name": "Amit Yadav", "roll_no": "11B02", "parent_name": "Ravi Yadav", "parent_phone": "+919800000004", "batch_id": 2, "address": "12 Gomti Nagar, Lucknow", "student_class": "11", "stream": "PCM", "board": "UP Board", "subject_fees": [{"subject": "Physics", "fee": 1800}, {"subject": "Chemistry", "fee": 1800}, {"subject": "Maths", "fee": 1800}], "total_fee": 5400, "joining_date": "2026-04-01", "status": "active", "created_at": "2026-04-01T00:00:00Z"},
        {"id": 5, "name": "Sneha Tiwari", "roll_no": "12C01", "parent_name": "Prem Tiwari", "parent_phone": "+919800000005", "batch_id": 3, "address": "56 Hazratganj, Lucknow", "student_class": "12", "stream": "PCB", "board": "CBSE", "subject_fees": [{"subject": "Physics", "fee": 2200}, {"subject": "Chemistry", "fee": 2200}, {"subject": "Biology", "fee": 2200}], "total_fee": 6600, "joining_date": "2026-04-01", "status": "active", "created_at": "2026-04-01T00:00:00Z"},
    ],
    "attendance": [],
    "message_logs": [],
    "fees": [
        {"id": 1, "student_id": 1, "total_fee": 3000, "installments": 3, "amount_paid": 1000, "due_date": "2026-12-01", "status": "Partial", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-04-01T00:00:00Z"},
        {"id": 2, "student_id": 2, "total_fee": 4000, "installments": 3, "amount_paid": 4000, "due_date": "2026-12-01", "status": "Paid", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-04-01T00:00:00Z"},
        {"id": 3, "student_id": 3, "total_fee": 6000, "installments": 3, "amount_paid": 0, "due_date": "2026-12-01", "status": "Pending", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-04-01T00:00:00Z"},
        {"id": 4, "student_id": 4, "total_fee": 5400, "installments": 3, "amount_paid": 5400, "due_date": "2026-12-01", "status": "Paid", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-04-01T00:00:00Z"},
        {"id": 5, "student_id": 5, "total_fee": 6600, "installments": 3, "amount_paid": 3300, "due_date": "2026-12-01", "status": "Partial", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-04-01T00:00:00Z"},
    ],
    "fee_payments": [],
    "audit_logs": [],
    "institute_settings": [
        {
            "id": 1,
            "institute_name": "Apex Coaching Institute",
            "institute_phone": "+919876543210",
            "institute_address": "123 Education Hub, Lucknow, UP",
            "whatsapp_provider": "mock",
            "absent_message_template": "Dear Parent, your ward {student_name} was absent from {batch_name} on {date}. Please ensure regular attendance.",
            "auto_send_absent_alerts": True,
            "updated_at": "2026-01-01T00:00:00Z"
        }
    ]
}

def load_store() -> dict:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure all keys exist
                for key in DEFAULT_STORE:
                    if key not in data:
                        data[key] = DEFAULT_STORE[key]
                return data
        except Exception:
            pass
    # First run: save defaults
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_STORE, f, indent=2, default=str)
    return dict(DEFAULT_STORE)

def save_store(store: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, default=str)

# Load store at startup
store = load_store()

# ─────────────────────────────────────────
# HTTP Handler
# ─────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def send_json(self, code: int, data: dict):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, file_path: Path):
        try:
            with open(file_path, "rb") as f:
                body = f.read()
            ext = file_path.suffix.lower()
            mime = MIME_TYPES.get(ext, "application/octet-stream")
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            raw = self.rfile.read(length)
            try:
                return json.loads(raw)
            except Exception:
                return {}
        return {}

    # Auth removed — all routes are public
    def require_auth(self):
        return {"id": 1, "name": "Admin", "role": "ADMIN"}

    def require_admin(self):
        return {"id": 1, "name": "Admin", "role": "ADMIN"}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PUT(self):
        self.route("PUT")

    def do_DELETE(self):
        self.route("DELETE")

    def route(self, method: str):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        # API routes
        if path.startswith("/api/v1"):
            api_path = path[len("/api/v1"):]
            self.handle_api(method, api_path, qs)
            return

        # Static frontend
        if method == "GET":
            self.serve_static(path)

    # ─────────────────────────────────────────
    # Static File Serving
    # ─────────────────────────────────────────
    def serve_static(self, path: str):
        if not FRONTEND_DIST.exists():
            self.send_json(503, {"error": "Frontend not built yet. Run: cd frontend && npm run build"})
            return

        # Map path to file
        rel = path.lstrip("/")
        candidate = FRONTEND_DIST / rel

        if candidate.is_file():
            self.send_static(candidate)
        elif (candidate / "index.html").is_file():
            self.send_static(candidate / "index.html")
        else:
            # SPA fallback
            index = FRONTEND_DIST / "index.html"
            if index.exists():
                self.send_static(index)
            else:
                self.send_response(404)
                self.end_headers()

    # ─────────────────────────────────────────
    # API Router
    # ─────────────────────────────────────────
    def handle_api(self, method: str, path: str, qs: dict):
        global store

        # ── Batches ───────────────────────────
        if path == "/batches" and method == "GET":
            u = self.require_auth()
            if not u: return
            batches = store["batches"]
            if u.get("role") == "TEACHER":
                batches = [b for b in batches if b.get("teacher_id") == u["id"]]
            # Enrich with teacher name
            result = []
            for b in batches:
                teacher = next((t for t in store["users"] if t["id"] == b.get("teacher_id")), None)
                result.append({**b, "teacher_name": teacher["name"] if teacher else "—"})
            return self.send_json(200, {"success": True, "data": result})

        if path == "/batches" and method == "POST":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            with _store_lock:
                new_id = max((b["id"] for b in store["batches"]), default=0) + 1
                record = {
                    "id": new_id,
                    "name": body.get("name", ""),
                    "subject": body.get("subject", ""),
                    "timing": body.get("timing", ""),
                    "teacher_id": int(body.get("teacher_id", 0)),
                    "status": "active",
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
                }
                store["batches"].append(record)
                save_store(store)
            return self.send_json(201, {"success": True, "data": record})

        m = re.match(r"^/batches/(\d+)$", path)
        if m:
            bid = int(m.group(1))
            if method == "PUT":
                u = self.require_admin()
                if not u: return
                body = self.read_body()
                with _store_lock:
                    idx = next((i for i, b in enumerate(store["batches"]) if b["id"] == bid), None)
                    if idx is None:
                        return self.send_json(404, {"success": False, "error": "Batch not found."})
                    store["batches"][idx].update({k: v for k, v in body.items() if k not in ("id", "created_at")})
                    save_store(store)
                return self.send_json(200, {"success": True, "data": store["batches"][idx]})
            if method == "DELETE":
                u = self.require_admin()
                if not u: return
                with _store_lock:
                    store["batches"] = [b for b in store["batches"] if b["id"] != bid]
                    save_store(store)
                return self.send_json(200, {"success": True, "message": "Batch deleted."})

        # ── Students ──────────────────────────
        if path == "/students" and method == "GET":
            u = self.require_auth()
            if not u: return
            students = [s for s in store["students"] if s.get("status") == "active"]
            # Filter by batch_id
            if "batch_id" in qs:
                bid = int(qs["batch_id"][0])
                students = [s for s in students if s.get("batch_id") == bid]
            # Search
            if "search" in qs:
                q_lower = qs["search"][0].lower()
                students = [s for s in students if q_lower in s.get("name", "").lower() or q_lower in s.get("roll_no", "").lower()]
            # Enrich with batch name
            result = []
            for s in students:
                batch = next((b for b in store["batches"] if b["id"] == s.get("batch_id")), None)
                result.append({**s, "batch_name": batch["name"] if batch else "—"})
            return self.send_json(200, {"success": True, "data": result, "total": len(result)})

        if path == "/students" and method == "POST":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            with _store_lock:
                new_id = max((s["id"] for s in store["students"]), default=0) + 1
                subject_fees = body.get("subject_fees", [])
                if isinstance(subject_fees, str):
                    try: subject_fees = json.loads(subject_fees)
                    except: subject_fees = []
                record = {
                    "id": new_id,
                    "name": body.get("name", ""),
                    "roll_no": body.get("roll_no", f"S{new_id:04d}"),
                    "parent_name": body.get("parent_name", ""),
                    "parent_phone": body.get("parent_phone", ""),
                    "batch_id": int(body.get("batch_id", 0)),
                    "address": body.get("address", ""),
                    "student_class": body.get("student_class"),
                    "stream": body.get("stream"),
                    "board": body.get("board"),
                    "subject_fees": subject_fees,
                    "total_fee": float(body.get("total_fee", 0)),
                    "joining_date": body.get("joining_date") or datetime.date.today().isoformat(),
                    "status": "active",
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
                }
                store["students"].append(record)
                # Auto-create fee record
                fee_record = {
                    "id": max((f["id"] for f in store["fees"]), default=0) + 1,
                    "student_id": new_id,
                    "total_fee": record["total_fee"],
                    "installments": 3,
                    "amount_paid": 0,
                    "due_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                    "status": "Pending",
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "updated_at": datetime.datetime.utcnow().isoformat() + "Z"
                }
                store["fees"].append(fee_record)
                save_store(store)
            return self.send_json(201, {"success": True, "data": record})

        m = re.match(r"^/students/(\d+)$", path)
        if m:
            sid = int(m.group(1))
            if method == "PUT":
                u = self.require_admin()
                if not u: return
                body = self.read_body()
                with _store_lock:
                    idx = next((i for i, s in enumerate(store["students"]) if s["id"] == sid), None)
                    if idx is None:
                        return self.send_json(404, {"success": False, "error": "Student not found."})
                    store["students"][idx].update({k: v for k, v in body.items() if k not in ("id", "created_at")})
                    save_store(store)
                return self.send_json(200, {"success": True, "data": store["students"][idx]})
            if method == "DELETE":
                u = self.require_admin()
                if not u: return
                with _store_lock:
                    idx = next((i for i, s in enumerate(store["students"]) if s["id"] == sid), None)
                    if idx is None:
                        return self.send_json(404, {"success": False, "error": "Student not found."})
                    store["students"][idx]["status"] = "inactive"
                    save_store(store)
                return self.send_json(200, {"success": True, "message": "Student removed."})

        # ── Teachers ──────────────────────────
        if path == "/teachers" and method == "GET":
            u = self.require_admin()
            if not u: return
            teachers = [t for t in store["users"] if t.get("role") == "TEACHER"]
            safe = [{k: v for k, v in t.items() if k != "password_hash"} for t in teachers]
            return self.send_json(200, {"success": True, "data": safe})

        if path == "/teachers" and method == "POST":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            with _store_lock:
                new_id = max((t["id"] for t in store["users"]), default=0) + 1
                pw = body.get("password") or "teacher123"
                record = {
                    "id": new_id,
                    "name": body.get("name", ""),
                    "email": body.get("email", ""),
                    "phone": body.get("phone", ""),
                    "password_hash": hash_password(pw),
                    "role": "TEACHER",
                    "status": "active",
                    "created_at": datetime.datetime.utcnow().isoformat() + "Z"
                }
                store["users"].append(record)
                save_store(store)
            safe = {k: v for k, v in record.items() if k != "password_hash"}
            return self.send_json(201, {"success": True, "data": safe})

        m = re.match(r"^/teachers/(\d+)$", path)
        if m:
            tid = int(m.group(1))
            if method == "DELETE":
                u = self.require_admin()
                if not u: return
                with _store_lock:
                    idx = next((i for i, t in enumerate(store["users"]) if t["id"] == tid and t.get("role") == "TEACHER"), None)
                    if idx is None:
                        return self.send_json(404, {"success": False, "error": "Teacher not found."})
                    store["users"][idx]["status"] = "inactive"
                    save_store(store)
                return self.send_json(200, {"success": True, "message": "Teacher removed."})

        # ── Attendance ────────────────────────
        if path == "/attendance/batch-roster" and method == "GET":
            u = self.require_auth()
            if not u: return
            batch_id = int((qs.get("batch_id") or ["0"])[0])
            date = (qs.get("date") or [datetime.date.today().isoformat()])[0]
            students = [s for s in store["students"] if s.get("batch_id") == batch_id and s.get("status") == "active"]
            att_today = {a["student_id"]: a["status"] for a in store["attendance"] if a.get("batch_id") == batch_id and a.get("date") == date}
            roster = [{**s, "attendance_status": att_today.get(s["id"])} for s in students]
            return self.send_json(200, {"success": True, "data": roster})

        if path == "/attendance/submit" and method == "POST":
            u = self.require_auth()
            if not u: return
            body = self.read_body()
            batch_id = int(body.get("batch_id", 0))
            date = body.get("date", datetime.date.today().isoformat())
            records = body.get("records", [])
            with _store_lock:
                for rec in records:
                    student_id = int(rec.get("student_id", 0))
                    status = rec.get("status", "P")
                    idx = next((i for i, a in enumerate(store["attendance"]) if a.get("student_id") == student_id and a.get("batch_id") == batch_id and a.get("date") == date), None)
                    entry = {"id": int(time.time() * 1000) + student_id, "student_id": student_id, "batch_id": batch_id, "date": date, "status": status, "marked_by": u["id"], "created_at": datetime.datetime.utcnow().isoformat() + "Z"}
                    if idx is not None:
                        store["attendance"][idx] = entry
                    else:
                        store["attendance"].append(entry)
                save_store(store)
            return self.send_json(200, {"success": True, "message": "Attendance saved."})

        if path == "/attendance/absent-list" and method == "GET":
            u = self.require_auth()
            if not u: return
            batch_id = int((qs.get("batch_id") or ["0"])[0])
            date = (qs.get("date") or [datetime.date.today().isoformat()])[0]
            absent_ids = {a["student_id"] for a in store["attendance"] if a.get("batch_id") == batch_id and a.get("date") == date and a.get("status") == "A"}
            absent_students = [s for s in store["students"] if s["id"] in absent_ids]
            batch = next((b for b in store["batches"] if b["id"] == batch_id), {})
            result = [{**s, "batch_name": batch.get("name", "—")} for s in absent_students]
            return self.send_json(200, {"success": True, "data": result})

        # ── Messages ──────────────────────────
        if path == "/messages/send-absent-broadcast" and method == "POST":
            u = self.require_auth()
            if not u: return
            body = self.read_body()
            batch_id = int(body.get("batch_id", 0))
            date = body.get("date", datetime.date.today().isoformat())
            absent_ids = {a["student_id"] for a in store["attendance"] if a.get("batch_id") == batch_id and a.get("date") == date and a.get("status") == "A"}
            absent_students = [s for s in store["students"] if s["id"] in absent_ids]
            batch = next((b for b in store["batches"] if b["id"] == batch_id), {})
            sent = []
            with _store_lock:
                for s in absent_students:
                    log_id = int(time.time() * 1000) + s["id"]
                    msg = f"Dear Parent, your ward {s['name']} was absent from {batch.get('name','—')} on {date}. Please ensure regular attendance. - Apex Institute"
                    log = {"id": log_id, "student_id": s["id"], "student_name": s["name"], "batch_id": batch_id, "date": date, "recipient_phone": s.get("parent_phone"), "message_body": msg, "status": "sent", "provider": "mock", "created_at": datetime.datetime.utcnow().isoformat() + "Z"}
                    store["message_logs"].append(log)
                    sent.append(log)
                save_store(store)
            return self.send_json(200, {"success": True, "data": {"sent": len(sent), "logs": sent}})

        if path == "/messages/logs" and method == "GET":
            u = self.require_auth()
            if not u: return
            batch_id = int((qs.get("batch_id") or ["0"])[0])
            date = (qs.get("date") or [""])[0]
            logs = store["message_logs"]
            if batch_id: logs = [l for l in logs if l.get("batch_id") == batch_id]
            if date: logs = [l for l in logs if l.get("date") == date]
            return self.send_json(200, {"success": True, "data": logs})

        # ── Dashboard ─────────────────────────
        if path == "/dashboard/stats" and method == "GET":
            u = self.require_admin()
            if not u: return
            date = (qs.get("date") or [datetime.date.today().isoformat()])[0]
            active_students = [s for s in store["students"] if s.get("status") == "active"]
            today_att = [a for a in store["attendance"] if a.get("date") == date]
            present = sum(1 for a in today_att if a.get("status") == "P")
            absent = sum(1 for a in today_att if a.get("status") == "A")
            total_fees = sum(f.get("total_fee", 0) for f in store["fees"])
            collected = sum(f.get("amount_paid", 0) for f in store["fees"])
            return self.send_json(200, {"success": True, "data": {
                "total_students": len(active_students),
                "total_batches": len([b for b in store["batches"] if b.get("status") == "active"]),
                "present_today": present,
                "absent_today": absent,
                "total_fees": total_fees,
                "fees_collected": collected,
                "fees_pending": total_fees - collected
            }})

        if path == "/dashboard/batch-summary" and method == "GET":
            u = self.require_admin()
            if not u: return
            date = (qs.get("date") or [datetime.date.today().isoformat()])[0]
            result = []
            for b in store["batches"]:
                if b.get("status") != "active": continue
                students = [s for s in store["students"] if s.get("batch_id") == b["id"] and s.get("status") == "active"]
                att = [a for a in store["attendance"] if a.get("batch_id") == b["id"] and a.get("date") == date]
                present = sum(1 for a in att if a.get("status") == "P")
                result.append({**b, "total_students": len(students), "present": present, "absent": len(students) - present})
            return self.send_json(200, {"success": True, "data": result})

        if path == "/dashboard/absent-grouped" and method == "GET":
            u = self.require_admin()
            if not u: return
            date = (qs.get("date") or [datetime.date.today().isoformat()])[0]
            result = []
            for b in store["batches"]:
                absent_ids = {a["student_id"] for a in store["attendance"] if a.get("batch_id") == b["id"] and a.get("date") == date and a.get("status") == "A"}
                absent_students = [s for s in store["students"] if s["id"] in absent_ids]
                if absent_students:
                    result.append({"batch": b, "absent_students": absent_students})
            return self.send_json(200, {"success": True, "data": result})

        # ── Settings ──────────────────────────
        if path == "/settings" and method == "GET":
            u = self.require_auth()
            if not u: return
            settings = store["institute_settings"][0] if store["institute_settings"] else {}
            return self.send_json(200, {"success": True, "data": settings})

        if path == "/settings" and method == "PUT":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            with _store_lock:
                if store["institute_settings"]:
                    store["institute_settings"][0].update({k: v for k, v in body.items() if k not in ("id",)})
                    store["institute_settings"][0]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                else:
                    store["institute_settings"] = [{**body, "id": 1, "updated_at": datetime.datetime.utcnow().isoformat() + "Z"}]
                save_store(store)
            return self.send_json(200, {"success": True, "data": store["institute_settings"][0]})

        # ── Fees ──────────────────────────────
        if path == "/fees" and method == "GET":
            u = self.require_auth()
            if not u: return
            fees = store["fees"]
            if "batch_id" in qs:
                bid = int(qs["batch_id"][0])
                student_ids = {s["id"] for s in store["students"] if s.get("batch_id") == bid and s.get("status") == "active"}
                fees = [f for f in fees if f.get("student_id") in student_ids]
            # Enrich with student name, batch
            result = []
            for f in fees:
                student = next((s for s in store["students"] if s["id"] == f.get("student_id")), None)
                if not student or student.get("status") != "active": continue
                batch = next((b for b in store["batches"] if b["id"] == student.get("batch_id")), {})
                result.append({**f, "student_name": student["name"] if student else "—", "batch_name": batch.get("name", "—"), "parent_phone": student.get("parent_phone") if student else ""})
            return self.send_json(200, {"success": True, "data": result})

        if path == "/fees/summary" and method == "GET":
            u = self.require_auth()
            if not u: return
            total = sum(f.get("total_fee", 0) for f in store["fees"])
            collected = sum(f.get("amount_paid", 0) for f in store["fees"])
            pending = total - collected
            paid_count = sum(1 for f in store["fees"] if f.get("status") == "Paid")
            partial_count = sum(1 for f in store["fees"] if f.get("status") == "Partial")
            due_count = sum(1 for f in store["fees"] if f.get("status") == "Pending")
            return self.send_json(200, {"success": True, "data": {"total_fee": total, "amount_collected": collected, "amount_pending": pending, "paid_count": paid_count, "partial_count": partial_count, "pending_count": due_count}})

        if path == "/fees/defaulters" and method == "GET":
            u = self.require_auth()
            if not u: return
            defaulters = [f for f in store["fees"] if f.get("status") in ("Pending", "Partial")]
            result = []
            for f in defaulters:
                student = next((s for s in store["students"] if s["id"] == f.get("student_id") and s.get("status") == "active"), None)
                if not student: continue
                batch = next((b for b in store["batches"] if b["id"] == student.get("batch_id")), {})
                result.append({**f, "student_name": student["name"], "batch_name": batch.get("name", "—"), "parent_phone": student.get("parent_phone", ""), "outstanding": f.get("total_fee", 0) - f.get("amount_paid", 0)})
            return self.send_json(200, {"success": True, "data": result})

        if path == "/fees/record-payment" and method == "POST":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            student_id = int(body.get("student_id", 0))
            amount = float(body.get("amount", 0))
            receipt_number = body.get("receipt_number") or f"RCP-{int(time.time())}"
            with _store_lock:
                fee_idx = next((i for i, f in enumerate(store["fees"]) if f.get("student_id") == student_id), None)
                if fee_idx is None:
                    return self.send_json(404, {"success": False, "error": "Fee record not found."})
                fee = store["fees"][fee_idx]
                new_paid = fee.get("amount_paid", 0) + amount
                new_status = "Paid" if new_paid >= fee.get("total_fee", 0) else "Partial"
                store["fees"][fee_idx]["amount_paid"] = new_paid
                store["fees"][fee_idx]["status"] = new_status
                store["fees"][fee_idx]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                payment = {"id": int(time.time() * 1000), "student_id": student_id, "amount": amount, "payment_date": body.get("payment_date") or datetime.date.today().isoformat(), "payment_mode": body.get("payment_mode", "Cash"), "receipt_number": receipt_number, "notes": body.get("notes", ""), "recorded_by": u["id"], "created_at": datetime.datetime.utcnow().isoformat() + "Z"}
                if "fee_payments" not in store: store["fee_payments"] = []
                store["fee_payments"].append(payment)
                save_store(store)
            return self.send_json(200, {"success": True, "data": {"payment": payment, "fee": store["fees"][fee_idx]}})

        m = re.match(r"^/fees/receipt/(.+)$", path)
        if m and method == "GET":
            u = self.require_auth()
            if not u: return
            receipt_no = unquote(m.group(1))
            payment = next((p for p in store.get("fee_payments", []) if p.get("receipt_number") == receipt_no), None)
            if not payment:
                return self.send_json(404, {"success": False, "error": "Receipt not found."})
            student = next((s for s in store["students"] if s["id"] == payment["student_id"]), {})
            batch = next((b for b in store["batches"] if b["id"] == student.get("batch_id")), {})
            settings = store["institute_settings"][0] if store["institute_settings"] else {}
            return self.send_json(200, {"success": True, "data": {"payment": payment, "student": student, "batch": batch, "institute": settings}})

        if path == "/fees/send-reminder-broadcast" and method == "POST":
            u = self.require_admin()
            if not u: return
            body = self.read_body()
            defaulters = [f for f in store["fees"] if f.get("status") in ("Pending", "Partial")]
            sent = 0
            for f in defaulters:
                student = next((s for s in store["students"] if s["id"] == f["student_id"] and s.get("status") == "active"), None)
                if student:
                    sent += 1
            return self.send_json(200, {"success": True, "data": {"sent": sent, "message": f"Fee reminders sent to {sent} parents (mock mode)."}})

        # ── 404 ───────────────────────────────
        self.send_json(404, {"success": False, "error": f"API route not found: {path}"})


# ─────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────
if __name__ == "__main__":
    # Verify Python password for default users on startup
    admin_hash = store["users"][0]["password_hash"]
    if not admin_hash.startswith("sha256$"):
        # Rehash with our format (old bcrypt hash from Node backend)
        store["users"][0]["password_hash"] = hash_password("admin123")
    if len(store["users"]) > 1:
        teacher_hash = store["users"][1]["password_hash"]
        if not teacher_hash.startswith("sha256$"):
            store["users"][1]["password_hash"] = hash_password("teacher123")
    save_store(store)

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"")
    print(f"  Apex Institute Server")
    print(f"  Running at: http://localhost:{PORT}")
    print(f"  API base:   http://localhost:{PORT}/api/v1")
    print(f"  Frontend:   {'http://localhost:' + str(PORT) if FRONTEND_DIST.exists() else 'Not built - run: cd frontend && npm run build'}")
    print(f"")
    print(f"  Demo credentials:")
    print(f"    Admin:   admin@apex.com  /  admin123")
    print(f"    Teacher: rahul@apex.com  /  teacher123")
    print(f"")
    print(f"  Press Ctrl+C to stop.")
    print(f"")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()
