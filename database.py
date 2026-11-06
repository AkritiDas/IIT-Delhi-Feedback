import json
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

# Check if PyMySQL is available
try:
    import pymysql
    import pymysql.cursors
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

class DatabaseManager:
    """
    Unified Database Manager for IIT Delhi Virtual Labs Feedback Portal.
    Supports both MySQL (production) and SQLite (automatic fallback/local development).
    """

    def __init__(self):
        self.engine_type = None
        self._detect_engine()

    def _detect_engine(self):
        """Detect whether MySQL is available and accessible, otherwise fallback to SQLite."""
        if Config.DB_TYPE == "sqlite":
            self.engine_type = "sqlite"
            logger.info("Using SQLite database by explicit configuration.")
            return

        if HAS_PYMYSQL and Config.DB_TYPE in ("mysql", "auto"):
            try:
                conn = pymysql.connect(
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    charset="utf8mb4",
                    connect_timeout=3
                )
                conn.close()
                self.engine_type = "mysql"
                logger.info("Connected successfully to MySQL database.")
                return
            except Exception as e:
                logger.warning(f"MySQL connection failed ({e}). Falling back to SQLite.")

        self.engine_type = "sqlite"
        logger.info("Using SQLite database engine.")

    def get_connection(self):
        """Return an active connection and cursor dict/factory for the active engine."""
        if self.engine_type == "mysql":
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn, "mysql"
        else:
            # Ensure database directory exists
            db_path = Path(Config.SQLITE_DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            return conn, "sqlite"

    def init_database(self, seed_demo=True):
        """Create tables if they do not exist and optionally seed demonstration records."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            if engine == "mysql":
                # MySQL Table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS virtual_labs_feedback (
                        feedback_id INT AUTO_INCREMENT PRIMARY KEY,
                        reference_id VARCHAR(32) NOT NULL UNIQUE,
                        full_name VARCHAR(150) NULL,
                        email VARCHAR(150) NULL,
                        mobile_number VARCHAR(30) NULL,
                        user_type VARCHAR(50) NOT NULL DEFAULT 'Student',
                        subject VARCHAR(100) NOT NULL,
                        experiment_name VARCHAR(255) NOT NULL,
                        experiment_url VARCHAR(500) NULL,
                        device VARCHAR(50) NOT NULL DEFAULT 'Laptop',
                        browser VARCHAR(50) NOT NULL DEFAULT 'Chrome',
                        overall_rating INT NOT NULL,
                        experiment_rating INT NOT NULL,
                        navigation_rating INT NOT NULL,
                        technical_rating INT NOT NULL,
                        selected_issues JSON NULL,
                        technical_details TEXT NULL,
                        experience_description TEXT NOT NULL,
                        positive_experience TEXT NULL,
                        improvement_suggestions TEXT NULL,
                        recommendation VARCHAR(20) NOT NULL DEFAULT 'Yes',
                        anonymous_status INT NOT NULL DEFAULT 0,
                        screenshot_paths JSON NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_ref (reference_id),
                        INDEX idx_subj (subject),
                        INDEX idx_rating (overall_rating)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            else:
                # SQLite Table creation
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS virtual_labs_feedback (
                        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        reference_id TEXT NOT NULL UNIQUE,
                        full_name TEXT NULL,
                        email TEXT NULL,
                        mobile_number TEXT NULL,
                        user_type TEXT NOT NULL DEFAULT 'Student',
                        subject TEXT NOT NULL,
                        experiment_name TEXT NOT NULL,
                        experiment_url TEXT NULL,
                        device TEXT NOT NULL DEFAULT 'Laptop',
                        browser TEXT NOT NULL DEFAULT 'Chrome',
                        overall_rating INTEGER NOT NULL,
                        experiment_rating INTEGER NOT NULL,
                        navigation_rating INTEGER NOT NULL,
                        technical_rating INTEGER NOT NULL,
                        selected_issues TEXT NULL,
                        technical_details TEXT NULL,
                        experience_description TEXT NOT NULL,
                        positive_experience TEXT NULL,
                        improvement_suggestions TEXT NULL,
                        recommendation TEXT NOT NULL DEFAULT 'Yes',
                        anonymous_status INTEGER NOT NULL DEFAULT 0,
                        screenshot_paths TEXT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()

            # Seed demo data if table is completely empty
            cursor.execute("SELECT COUNT(*) AS total FROM virtual_labs_feedback")
            row = cursor.fetchone()
            count = row["total"] if isinstance(row, dict) else row[0]

            if count == 0 and seed_demo:
                self._seed_sample_records(cursor, engine)
                if engine == "sqlite":
                    conn.commit()
                logger.info("Database initialized and seeded with demo records.")
        finally:
            cursor.close()
            conn.close()

    def _seed_sample_records(self, cursor, engine):
        """Seed representative demonstration records."""
        demo_items = [
            (
                "IITD-VL-2026-DEMO01",
                "Aarav Sharma",
                "aarav.sharma@example.edu",
                "+91 9876543210",
                "Student",
                "Computer Science",
                "Binary Search Tree Visualization",
                "https://vlabs.iitd.ac.in/cse/bst",
                "Laptop",
                "Chrome",
                5, 5, 4, 5,
                json.dumps([]),
                "",
                "The step-by-step traversal animation helped clarify AVL node balancing and re-coloring before our semester exams.",
                "Smooth canvas animation, intuitive controls, and responsive UI.",
                "Include a downloadable algorithmic trace table as PDF.",
                "Yes",
                0,
                json.dumps([]),
                "2026-11-03 10:15:00"
            ),
            (
                "IITD-VL-2026-DEMO02",
                "Prof. Sunita Raman",
                "s.raman@iitd.ac.in",
                "+91 9811122334",
                "Faculty",
                "Electrical Engineering",
                "Three-Phase Induction Motor Speed Control",
                "https://vlabs.iitd.ac.in/ee/induction-motor",
                "Desktop",
                "Firefox",
                4, 4, 3, 4,
                json.dumps(["Simulation is not working", "Mobile responsiveness problem"]),
                "V/f controller slider lagged during peak load setting.",
                "Conducted virtual practical sessions with 70 undergraduates. The waveform analysis matched real laboratory dyno readings closely.",
                "Real-time oscillogram plotting is accurate and intuitive.",
                "Make slider controls easier to manipulate on touch displays.",
                "Yes",
                0,
                json.dumps([]),
                "2026-11-04 14:30:00"
            ),
            (
                "IITD-VL-2026-DEMO03",
                None,
                None,
                None,
                "Researcher",
                "Physics",
                "Michelson Interferometer Fringe Analysis",
                "https://vlabs.iitd.ac.in/phy/interferometer",
                "Laptop",
                "Edge",
                3, 3, 4, 2,
                json.dumps(["Website is loading slowly", "Display or layout issues"]),
                "Canvas WebGL context lost after 10 minutes of inactivity.",
                "The monochromatic light fringe shifts were mathematically consistent, but the simulation crashed when toggling sodium D-lines.",
                "Good theoretical background notes included in the tab.",
                "Optimize WebGL canvas memory usage for older graphics drivers.",
                "Maybe",
                1,
                json.dumps([]),
                "2026-11-05 16:45:00"
            )
        ]

        query = """
            INSERT INTO virtual_labs_feedback (
                reference_id, full_name, email, mobile_number, user_type,
                subject, experiment_name, experiment_url, device, browser,
                overall_rating, experiment_rating, navigation_rating, technical_rating,
                selected_issues, technical_details, experience_description,
                positive_experience, improvement_suggestions, recommendation,
                anonymous_status, screenshot_paths, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """
        if engine == "mysql":
            query = query.replace("?", "%s")

        for item in demo_items:
            cursor.execute(query, item)

    def insert_feedback(self, data):
        """Insert a validated feedback record."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO virtual_labs_feedback (
                    reference_id, full_name, email, mobile_number, user_type,
                    subject, experiment_name, experiment_url, device, browser,
                    overall_rating, experiment_rating, navigation_rating, technical_rating,
                    selected_issues, technical_details, experience_description,
                    positive_experience, improvement_suggestions, recommendation,
                    anonymous_status, screenshot_paths, created_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """
            if engine == "mysql":
                query = query.replace("?", "%s")

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            params = (
                data["reference_id"],
                data.get("full_name"),
                data.get("email"),
                data.get("mobile_number"),
                data.get("user_type", "Student"),
                data["subject"],
                data["experiment_name"],
                data.get("experiment_url"),
                data.get("device", "Laptop"),
                data.get("browser", "Chrome"),
                int(data["overall_rating"]),
                int(data["experiment_rating"]),
                int(data["navigation_rating"]),
                int(data["technical_rating"]),
                json.dumps(data.get("selected_issues", [])),
                data.get("technical_details", ""),
                data["experience_description"],
                data.get("positive_experience", ""),
                data.get("improvement_suggestions", ""),
                data.get("recommendation", "Yes"),
                1 if data.get("anonymous_status") else 0,
                json.dumps(data.get("screenshot_paths", [])),
                now_str
            )

            cursor.execute(query, params)
            if engine == "sqlite":
                conn.commit()
                feedback_id = cursor.lastrowid
            else:
                feedback_id = cursor.lastrowid

            return {
                "feedback_id": feedback_id,
                "reference_id": data["reference_id"]
            }
        finally:
            cursor.close()
            conn.close()

    def get_feedback_by_reference(self, reference_id):
        """Retrieve a specific record by its unique reference ID."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM virtual_labs_feedback WHERE reference_id = ?"
            if engine == "mysql":
                query = query.replace("?", "%s")
            cursor.execute(query, (reference_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._format_row(row)
        finally:
            cursor.close()
            conn.close()

    def get_feedback_by_id(self, feedback_id):
        """Retrieve a specific record by its integer primary key."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM virtual_labs_feedback WHERE feedback_id = ?"
            if engine == "mysql":
                query = query.replace("?", "%s")
            cursor.execute(query, (feedback_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._format_row(row)
        finally:
            cursor.close()
            conn.close()

    def get_all_feedback(self, filters=None):
        """Retrieve all feedback records matching optional filters."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            conditions = []
            params = []

            if filters:
                if filters.get("subject"):
                    conditions.append("subject = ?")
                    params.append(filters["subject"])
                if filters.get("rating"):
                    conditions.append("overall_rating = ?")
                    params.append(int(filters["rating"]))
                if filters.get("user_type"):
                    conditions.append("user_type = ?")
                    params.append(filters["user_type"])
                if filters.get("anonymous"):
                    val = 1 if filters["anonymous"] == "yes" else 0
                    conditions.append("anonymous_status = ?")
                    params.append(val)
                if filters.get("search"):
                    term = f"%{filters['search'].strip()}%"
                    conditions.append(
                        "(reference_id LIKE ? OR experiment_name LIKE ? OR full_name LIKE ? OR email LIKE ?)"
                    )
                    params.extend([term, term, term, term])

            base_query = "SELECT * FROM virtual_labs_feedback"
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            base_query += " ORDER BY created_at DESC"

            if engine == "mysql":
                base_query = base_query.replace("?", "%s")

            cursor.execute(base_query, tuple(params))
            rows = cursor.fetchall()

            result = []
            issue_filter = filters.get("issue") if filters else None
            for row in rows:
                formatted = self._format_row(row)
                if issue_filter:
                    if issue_filter not in formatted["selected_issues"]:
                        continue
                result.append(formatted)
            return result
        finally:
            cursor.close()
            conn.close()

    def get_feedback_stats(self):
        """Compute aggregate statistics for the admin dashboard and public hero cards."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM virtual_labs_feedback")
            rows = cursor.fetchall()

            total_count = len(rows)
            if total_count == 0:
                return {
                    "total_count": 0,
                    "avg_overall": 0.0,
                    "avg_experiment": 0.0,
                    "avg_navigation": 0.0,
                    "avg_technical": 0.0,
                    "anonymous_count": 0,
                    "identified_count": 0,
                    "rating_breakdown": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    "subject_distribution": {},
                    "issue_counts": {},
                    "recommendations": {"Yes": 0, "No": 0, "Maybe": 0}
                }

            sum_overall = 0
            sum_exp = 0
            sum_nav = 0
            sum_tech = 0
            anon_count = 0
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            subj_dist = {}
            issue_dist = {}
            recom_dist = {"Yes": 0, "No": 0, "Maybe": 0}

            for r in rows:
                row = self._format_row(r)
                ov = row["overall_rating"]
                sum_overall += ov
                sum_exp += row["experiment_rating"]
                sum_nav += row["navigation_rating"]
                sum_tech += row["technical_rating"]

                rating_dist[ov] = rating_dist.get(ov, 0) + 1

                if row["anonymous_status"]:
                    anon_count += 1

                subj = row["subject"]
                subj_dist[subj] = subj_dist.get(subj, 0) + 1

                recom = row["recommendation"]
                recom_dist[recom] = recom_dist.get(recom, 0) + 1

                for iss in row["selected_issues"]:
                    issue_dist[iss] = issue_dist.get(iss, 0) + 1

            return {
                "total_count": total_count,
                "avg_overall": round(sum_overall / total_count, 1),
                "avg_experiment": round(sum_exp / total_count, 1),
                "avg_navigation": round(sum_nav / total_count, 1),
                "avg_technical": round(sum_tech / total_count, 1),
                "anonymous_count": anon_count,
                "identified_count": total_count - anon_count,
                "rating_breakdown": rating_dist,
                "subject_distribution": subj_dist,
                "issue_counts": issue_dist,
                "recommendations": recom_dist
            }
        finally:
            cursor.close()
            conn.close()

    def delete_feedback(self, feedback_id):
        """Delete a feedback entry by ID."""
        conn, engine = self.get_connection()
        cursor = conn.cursor()
        try:
            # First fetch to get screenshots for disk cleanup
            record = self.get_feedback_by_id(feedback_id)
            if not record:
                return False, []

            query = "DELETE FROM virtual_labs_feedback WHERE feedback_id = ?"
            if engine == "mysql":
                query = query.replace("?", "%s")
            cursor.execute(query, (feedback_id,))
            if engine == "sqlite":
                conn.commit()
            return True, record.get("screenshot_paths", [])
        finally:
            cursor.close()
            conn.close()

    def _format_row(self, row):
        """Format raw DB row into dictionary with parsed JSON fields."""
        if isinstance(row, sqlite3.Row):
            data = dict(row)
        else:
            data = dict(row)

        # Parse selected_issues
        issues = data.get("selected_issues")
        if isinstance(issues, str):
            try:
                data["selected_issues"] = json.loads(issues)
            except Exception:
                data["selected_issues"] = []
        elif issues is None:
            data["selected_issues"] = []

        # Parse screenshot_paths
        screenshots = data.get("screenshot_paths")
        if isinstance(screenshots, str):
            try:
                data["screenshot_paths"] = json.loads(screenshots)
            except Exception:
                data["screenshot_paths"] = []
        elif screenshots is None:
            data["screenshot_paths"] = []

        # Format created_at to string if datetime
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return data

# Singleton instance
db_manager = DatabaseManager()

