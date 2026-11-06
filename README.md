# IIT Delhi Virtual Labs – Smart Feedback Portal

A comprehensive, production-grade, responsive academic feedback web application built for **IIT Delhi Virtual Labs** (under the National Mission on Education through ICT, Ministry of Education, Govt. of India).

Developed with **Python Flask**, **MySQL** (with automatic zero-config **SQLite** fallback), modern HTML5/CSS3/JavaScript, and an IIT Delhi-inspired academic design language (maroon, charcoal, white, and subtle saffron).

---

## 🏛️ Key Features

### 1. Unique Academic Interface & Theming
- **Palette**: IIT Delhi Maroon (`#7B1113`, `#56080A`, `#991B1E`), Charcoal (`#0F172A`, `#1E293B`), Clean White, and Saffron accents (`#E65100`, `#F59E0B`).
- **Typography**: Modern Google Fonts (*Outfit* headings & *Plus Jakarta Sans* body).
- **Dark/Light Mode**: Instant theme switcher with `localStorage` persistence and accessible contrast.
- **Responsive Layout**: Designed for mobile devices, tablets, laptops, and ultra-wide desktops.
- **Bespoke Academic Insignia**: Custom SVG academic badge (compliant with guidelines; no unauthorized copyrighted logos).

### 2. Header, Navigation & Hero Section
- **Live Status Indicator**: Animated green pulsing beacon ("Feedback Cycle 2026 Active • We value your feedback").
- **Navigation Bar**: Quick links to Home, About Virtual Labs, Give Feedback, Guidelines, and Contact.
- **Hero Section**: Prominent call-to-actions, feedback guidelines modal, and illustrative demonstration benchmark cards (12+ disciplines, 180+ simulations, 4.8★ avg rating, 99.8% uptime).

### 3. Comprehensive Multi-Section Feedback Form
- **Form Completion Progress Bar**: Real-time percentage indicator updating dynamically as fields are filled.
- **Anonymous Feedback Toggle**: Switch to anonymous mode to automatically hide and omit personal information.
- **Section A: Personal Information**: Full Name, Email, Mobile Number with Country Code, and User Type (Student, Faculty, Researcher, Other).
- **Section B: Virtual Lab Information**: Laboratory/Subject selector, Experiment Name, Experiment URL, Device used (Desktop, Laptop, Tablet, Mobile), Browser used (Chrome, Firefox, Edge, Safari, Other).
- **Section C: Star Rating System**: Interactive 5-star ratings across 4 distinct dimensions:
  1. *Overall Experience*
  2. *Quality of Experiment*
  3. *Ease of Navigation*
  4. *Technical Performance*
  (Includes star hover animations, rating badges like "4/5 - Very Good", keyboard accessibility, and mobile touch support).
- **Section D: Issue Selection & Smart Conditional Diagnostics**:
  - Interactive multi-select cards for 13 problem categories (simulation not working, loading slowly, broken links, audio/video, etc.).
  - "Other" reveals a dedicated specification field.
  - **Smart Conditional Question**: Selecting any technical issue automatically reveals a diagnostic prompt requesting stage-specific failure details.
- **Section E: Share Your Experience**:
  - Detailed qualitative textarea with live character counter (min 10 chars, max 2000 chars, color-coded progress).
  - Optional positive highlights and improvement suggestions.
- **Section F: Drag-and-Drop Screenshot Upload**:
  - Upload multiple screenshots (PNG, JPG, JPEG, WEBP; up to 10 MB each).
  - Real-time client-side thumbnail previews with formatted file sizes.
  - Instant remove button (`✕`) per attached image.
  - Secure server-side validation and UUID-prefixed file storage.
- **Section G: Additional Suggestions & Recommendation**:
  - Net Promoter style recommendation pills (*Yes, Highly* / *Maybe* / *No*).
- **Preview Feedback Modal**: Review all entered details before committing.
- **Form Reset with Confirmation**: Safeguards against accidental data loss.

### 4. Submission & Receipt System
- Duplicate submission prevention and animated loading spinner.
- Generation of unique reference ID: `IITD-VL-2026-XXXXXX`.
- Dedicated receipt page (`/feedback/<reference_id>`) with printable acknowledgment slip.

### 5. Secure Administrator Portal (`/admin/dashboard`)
- Protected by session authentication.
- **Analytics Metrics**: Total submissions, average ratings across all dimensions, anonymous ratio, recommendation percentages.
- **Interactive Visualizations (Chart.js)**:
  - Subject distribution (Doughnut chart)
  - Rating breakdown (Bar chart, 1★ to 5★)
  - Top reported issues (Horizontal bar chart)
- **Advanced Filtering & Search**:
  - Search by Reference ID, Contributor Name, Email, or Experiment.
  - Filter by Subject, Star Rating, User Type, and Reported Issue.
- **Detailed Modal Inspector**: Inspect complete feedback, diagnostic logs, and view attached screenshots with full-size zoom.
- **CSV Data Export**: One-click export of filtered feedback records (`/admin/export/csv`).
- **Record Deletion**: Delete records and clean up associated screenshot files from disk.

---

## 📁 Project Structure

```
IIT Delhi Feedback/
│
├── app.py                      # Core Flask application, routing, and APIs
├── config.py                   # Configuration management & environment loading
├── database.py                 # Unified database manager (MySQL + SQLite fallback)
├── test_portal.py              # Automated test suite (6 unit & integration tests)
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── .env                        # Active environment variables
│
├── templates/
│   ├── index.html              # Main public feedback portal page
│   ├── success.html            # Submission confirmation & printable receipt
│   ├── admin_login.html        # Administrator sign-in portal
│   ├── admin_dashboard.html    # Administrator analytics & record management
│   └── 404.html                # Custom academic 404 error page
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom academic CSS (IIT maroon theme, dark mode)
│   ├── js/
│   │   └── script.js           # Star rating, previews, progress bar, validations
│   └── uploads/                # Directory storing uploaded screenshots
│
└── database/
    ├── schema.sql              # MySQL DDL schema and sample demo data
    ├── init_db.py              # CLI database initialization and verification script
    └── feedback.db             # Local SQLite database (auto-created on first run)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+** installed.
- (Optional) **MySQL 8.0+** or **MariaDB 10.4+** (if using MySQL).

### 2. Installation
Open your terminal in the project directory and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

The application is engineered to work **out-of-the-box**:
- **Automatic Fallback (Zero Config)**: By default, `DB_TYPE=auto`. If MySQL is not running or not configured, the app automatically initializes an SQLite database at `database/feedback.db` with identical tables and seed data.
- **Connecting to MySQL**:
  1. Open MySQL and run `database/schema.sql`:
     ```bash
     mysql -u root -p < database/schema.sql
     ```
  2. Configure your MySQL credentials in `.env`:
     ```env
     DB_TYPE=mysql
     DB_HOST=localhost
     DB_PORT=3306
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_NAME=iitd_feedback
     ```
  3. Verify database initialization:
     ```bash
     python database/init_db.py
     ```

### 4. Running the Application
Launch the Flask development server:

```bash
python app.py
```

The portal will be live at:
- **Public Feedback Portal**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Sign In**: [http://127.0.0.1:5000/admin/login](http://127.0.0.1:5000/admin/login)

---

## 🔐 Administrator Credentials

| Role | Username | Password |
|---|---|---|
| **Quality Portal Administrator** | `admin` | `admin@iitd2026` |

*(Credentials can be customized in `.env` using `ADMIN_USERNAME` and `ADMIN_PASSWORD`)*.

---

## 🧪 Running Automated Tests

Run the comprehensive end-to-end test suite:

```bash
python test_portal.py
```

**Test Coverage Includes:**
- Public landing page rendering and branding checks.
- Non-anonymous feedback submission with ratings and mock screenshot upload.
- Anonymous mode verification (ensuring personal contact fields are omitted).
- Server-side validation enforcement (short descriptions, missing ratings, invalid formats).
- Admin authentication, route protection, metric queries, inspection API, and CSV export.
- Public submission receipt generation.

---

## 🛡️ Security & Quality Best Practices
- **Parameterized SQL**: All database queries use parameterized placeholders (`%s` in MySQL, `?` in SQLite) to prevent SQL injection.
- **Secure File Uploads**: File extensions and MIME types are strictly validated; files are stored using randomized UUID filenames via `werkzeug.utils.secure_filename`.
- **Session Authentication**: Admin routes are protected using session verification decorators.
- **Credential Protection**: Database passwords and application secrets are managed strictly through environment variables.

