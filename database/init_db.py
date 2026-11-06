"""
Database Initialization Script for IIT Delhi Virtual Labs Feedback Portal.
Can be executed to verify database connection, create tables, and populate demo records.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import db_manager

def main():
    print("=" * 65)
    print("IIT Delhi Virtual Labs – Feedback Portal DB Setup")
    print("=" * 65)
    print(f"Detected Engine: {db_manager.engine_type.upper()}")
    
    try:
        db_manager.init_database(seed_demo=True)
        print("✓ Database table created and initialized successfully.")
        
        stats = db_manager.get_feedback_stats()
        print(f"✓ Initial records count: {stats['total_count']}")
        print(f"✓ Overall average rating: {stats['avg_overall']} / 5.0")
        print("=" * 65)
        print("Setup completed successfully.")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

