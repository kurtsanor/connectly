# Connectly 🔗

> A Django-powered REST API platform for modern social networking — built for speed, scale, and real human connection.

---

## 📌 Project Overview

**Connectly** is a full-featured social media backend built on **Django 6.0.1** and **Django REST Framework**. It provides a robust, scalable REST API that powers core social networking functionality: user identity, content publishing, social interactions, and personalized feeds.

Whether you're building a mobile app, a web client, or integrating social features into an existing product, Connectly delivers the API layer you need — secure, clean, and extensible.

---

## ✨ Core Features

### 👤 User Management
- **Registration & Authentication** — Secure sign-up/login with JWT token-based auth
- **Google OAuth** — One-click social login via Google OAuth 2.0
- **Avatar Uploads** — Profile images stored and served via Cloudinary
- **User Following** — Follow/unfollow users; query followers and following lists

### 📝 Posts
- **Rich Content Support** — Create and retrieve text, image, and video posts
- **Metadata** — Attach custom metadata to posts for extended context

### 💬 Social Interactions
- **Comments** — Threaded comment support on any post
- **Likes** — Like/unlike posts with like count tracking
- **Post Filters** — Filter feed by liked posts or posts from followed users

### 📰 Feed System
- **Personalized Feed** — Aggregated content from users you follow or posts you've liked
- **Pagination** — Efficient page-based pagination for large feeds

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 6.0.1 |
| **API** | Django REST Framework |
| **Authentication** | JWT (`djangorestframework-simplejwt`) + Google OAuth |
| **Media Storage** | Cloudinary |
| **Database** | SQLite (development) |
| **Password Hashing** | bcrypt |

---

## 🏗️ Project Architecture

```
connectly/
├── connectly_config/        # Main project settings & URL routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                   # Users app
│   ├── models.py            # User profiles & follow relationships
│   ├── serializers.py
│   ├── views.py             # Auth, registration, profile, follow endpoints
│   └── urls.py
│
├── posts/                   # Posts app
│   ├── models.py            # Post, Comment, Like models
│   ├── serializers.py
│   ├── views.py             # Post CRUD, comments, likes, feed
│   └── urls.py
│
└── manage.py
```

### App Breakdown

- **`users`** — Handles everything identity-related: registration, login (JWT & Google OAuth), profile management, avatar uploads, and the follow graph.
- **`posts`** — Manages the content layer: post creation and retrieval (text/image/video), comments, likes, feed generation, and post filtering.
- **`connectly_config`** — Central configuration: Django settings, middleware, installed apps, and top-level URL routing.

---

## 📡 API Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/login/` | Email & password login — returns JWT tokens |
| `GET` | `/auth/google/` | Get Google OAuth authorization URL |
| `GET` | `/auth/google/callback/` | OAuth redirect callback handler |
| `POST` | `/auth/google/login/` | Authenticate using a Google ID token |

### Users

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/` | List all users |
| `POST` | `/users/` | Register a new user |
| `POST` | `/users/avatar/` | Upload or update the authenticated user's avatar |
| `POST` | `/users/<user_id>/follow/` | Follow a user |

### Posts

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/posts/` | List all posts |
| `POST` | `/posts/` | Create a new post |
| `GET` | `/posts/<post_id>/` | Retrieve a single post |

### Comments

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/posts/<post_id>/comments/` | List all comments on a post |
| `POST` | `/posts/<post_id>/comment/` | Add a comment to a post |

### Likes & Feed

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/posts/<post_id>/like/` | Like a post |
| `GET` | `/feed/` | Get the personalized feed (paginated) |

---

## 🚀 Installation Guide

### Prerequisites

- Python 3.10+
- pip
- A [Cloudinary](https://cloudinary.com) account (for media uploads)
- A [Google Cloud](https://console.cloud.google.com) project (for OAuth)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/connectly.git
cd connectly
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback/
```

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

### 5. Initialize the Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at: **`http://127.0.0.1:8000/`**

---

## 🔐 Authentication

Connectly uses **JWT tokens** for API authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

Obtain tokens via:
- `POST /auth/login/` — Email & password login
- `POST /auth/google/login/` — Google OAuth login

---

> 📝 * This README was generated with AI assistance and reviewed/edited by the group. AI was also used to generate mock post data for pagination testing in Postman*
