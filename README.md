# TWINK — Realtime Chat App

A clean, minimal **Django + Channels** real-time chat application with personal and group chats, light/dark themes, and a modern Bootstrap 5 UI. This README is organized for clarity and copy-paste readiness so you can drop it directly into `README.md` in your repository.

---

## 🔥 Highlights

* ✅ Real-time messaging using **Django Channels** and WebSockets
* ✅ User registration, login, profile pictures & bios
* ✅ 1‑on‑1 (private) chats and group chats
* ✅ Light / Dark theme toggle across the UI
* ✅ Modern, responsive Bootstrap 5 interface inspired by Instagram/WhatsApp
* ✅ Optional **demo mode**: inject fake users/messages for a UI preview
* ✅ Ready for local development, testing and deployment

---

## 🖼️ Screenshots

Below are screenshots of key pages (place your images in `screenshots/`):

### Welcome Page

![Welcome Page](docs/screenshots/Welcome_Page.jpg)

### Login Page

![Login Page](docs/screenshots/Login_Page.jpg)

### Registration Page

![Registration Page](docs/screenshots/Register_Page.jpg)

### Settings

![Settings](docs/screenshots/Settings_Page1.jpg)

![Settings](docs/screenshots/Settings_Page2.jpg)

![Terms & Condition](docs/screenshots/TermsandCondition_Page.jpg)

### Home Page

![Home Page](docs/screenshots/Home_Page.jpg)

### Profile

![Profile](docs/screenshots/Profile_Page1.jpg)

![Edit\_Profile](docs/screenshots/EditProfile_Page.jpg)

---

## ⚙️ Features

### Authentication & Profiles

* Django built-in auth with username/email registration
* Profile model supports avatar (profile picture), bio and basic status
* Edit profile page with preview

### Chat System

* **Private chats** between two users
* **Group chats** (create, invite, leave)
* Messages include text, timestamps and read receipts
* Avatars and online indicators in chat lists
* Message ordering, typing indicators (UI), and message metadata

### UI & Theme

* Bootstrap 5 based responsive layout
* Light / Dark theme stored in localStorage so theme persists across visits
* Mobile-first design with chat list + message view split

### Demo Mode

* Optional JavaScript demo injector that creates fake users, groups and messages for demoing the UI
* Toggleable from `settings` or via a query param (`?demo=1`)

---

## 🧠 Tech Stack

| Layer      | Technology                                        |
| ---------- | ------------------------------------------------- |
| Backend    | Django 5.x, Django Channels                       |
| Frontend   | HTML, Bootstrap 5, CSS (custom theme), Vanilla JS |
| Database   | SQLite (default)                                  |
| Auth       | Django built-in authentication                    |
| Deployment | GitHub + PythonAnywhere/Render ready              |

---

## 🚀 Install & Run (Development)

1. **Clone the repo**

```bash
git clone https://github.com/<your-username>/TWINK.git
cd TWINK
```

2. **Create & activate virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Apply database migrations**

```bash
python manage.py migrate
```

5. **Create a superuser (optional)**

```bash
python manage.py createsuperuser
```

6. **Run development server**

```bash
python manage.py runserver
```

Visit 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Project Structure

```
TWINK/                            # repo root
├─ chat/                          # Django app for chat functionality
│  ├─ templates/chat/             # HTML templates (base, login, home, profile...)
│  ├─ static/chat/                # CSS, JS, images
│  ├─ models.py                   # Chat, Group, Profile models
│  ├─ consumers.py                # WebSocket consumers (channels)
│  ├─ routing.py                  # Channels routing
│  ├─ views.py                    # Views for pages & APIs
│  └─ forms.py                    # Registration & profile forms
├─ TWINK_proj/                    # Django project configuration
│  ├─ asgi.py                     # Channels ASGI entry
│  ├─ settings.py                 # Settings & channels config
│  └─ urls.py                     # Project URL routing
├─ docs/                          # screenshots and documentation assets
├─ requirements.txt               # Python dependencies
└─ README.md                      # this file
```

---

## 🔌 Channels Configuration

* `TWINK_proj/asgi.py` should load `channels.routing.ProtocolTypeRouter` and include `AuthMiddlewareStack` for WebSocket auth.
* For production-ready deployments, configure a channel layer like Redis and set `CHANNEL_LAYERS` in `settings.py`.

Example:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("127.0.0.1", 6379)]},
    },
}
```

---

## ✅ Demo Mode

Enable demo mode via Settings or add `?demo=1` to URL. It injects fake users/messages purely on the front-end for UI previews.

---

## 🧪 Testing

Run tests:

```bash
python manage.py test
```

---

## 🧩 Deployment

* Use Redis for Channels in production.
* Run with Daphne or Uvicorn:

```bash
daphne -b 0.0.0.0 -p 8000 TWINK_proj.asgi:application
```

* Serve static/media files with Nginx.
* Configure environment variables (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`).

---

## 🧑‍💻 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/awesome`
3. Commit & push: `git push origin feature/awesome`
4. Open a Pull Request

---

## 📝 License

MIT License — see `LICENSE` for details.

---

## 📬 Contact

Need help integrating this app (e.g., Docker, CI/CD, or React frontend)? Reach out and I’ll guide you through it.

---

*Made with ❤️ for TWINK — drop screenshots into `docs/screenshots/` and enjoy building!*
