#!/usr/bin/env python3
"""
Migration Script: In-Memory to PostgreSQL (Neon)
Migrates session storage from dictionary to persistent database
"""
import os
import sys
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:neon123@ep-xxx.eu-central-1.aws.neon.tech/iva_margem_turismo?sslmode=require")

print("🚀 IVA Margem Turismo - Database Migration")
print("=" * 50)

# Create engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define models
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_key = Column(String(50), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

def create_tables():
    """Create all tables in database"""
    print("📊 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

def create_indexes():
    """Create performance indexes"""
    print("🔍 Creating indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);",
        "CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at);",
    ]
    
    with engine.connect() as conn:
        for idx in indexes:
            try:
                conn.execute(text(idx))
                conn.commit()
                print(f"✅ Index created: {idx.split()[5]}")
            except Exception as e:
                print(f"⚠️  Index might already exist: {e}")

def create_cleanup_function():
    """Create automatic cleanup function for expired sessions"""
    print("🧹 Creating cleanup function...")
    
    cleanup_sql = """
    CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
    RETURNS INTEGER AS $$
    DECLARE
        deleted_count INTEGER;
    BEGIN
        DELETE FROM sessions 
        WHERE expires_at < CURRENT_TIMESTAMP;
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RETURN deleted_count;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(cleanup_sql))
            conn.commit()
        print("✅ Cleanup function created")
    except Exception as e:
        print(f"⚠️  Cleanup function might already exist: {e}")

def migrate_existing_data():
    """Migrate any existing session data"""
    print("📦 Checking for existing data to migrate...")
    
    # Check if we have any local session files
    temp_dir = "../temp"
    if os.path.exists(temp_dir):
        session_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        
        if session_files:
            print(f"Found {len(session_files)} session files to migrate")
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            
            migrated = 0
            for file in session_files:
                try:
                    with open(os.path.join(temp_dir, file), 'r') as f:
                        data = json.load(f)
                    
                    session = Session(
                        session_key=file.replace('.json', ''),
                        data=data,
                        created_at=datetime.fromtimestamp(os.path.getctime(os.path.join(temp_dir, file)))
                    )
                    
                    db.add(session)
                    migrated += 1
                except Exception as e:
                    print(f"⚠️  Error migrating {file}: {e}")
            
            try:
                db.commit()
                print(f"✅ Migrated {migrated} sessions")
            except Exception as e:
                print(f"❌ Error saving migrations: {e}")
                db.rollback()
            finally:
                db.close()
        else:
            print("ℹ️  No existing sessions to migrate")
    else:
        print("ℹ️  No temp directory found")

def test_connection():
    """Test database connection and operations"""
    print("\n🧪 Testing database operations...")
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Test 1: Create session
        test_session = Session(
            session_key="test-" + str(uuid.uuid4())[:8],
            data={
                "test": True,
                "timestamp": datetime.utcnow().isoformat(),
                "sales": [],
                "costs": []
            }
        )
        db.add(test_session)
        db.commit()
        print("✅ CREATE operation successful")
        
        # Test 2: Read session
        retrieved = db.query(Session).filter_by(session_key=test_session.session_key).first()
        if retrieved:
            print("✅ READ operation successful")
        
        # Test 3: Update session
        retrieved.data = {**retrieved.data, "updated": True}
        db.commit()
        print("✅ UPDATE operation successful")
        
        # Test 4: Delete session
        db.delete(retrieved)
        db.commit()
        print("✅ DELETE operation successful")
        
        # Test 5: Cleanup function
        result = db.execute(text("SELECT cleanup_expired_sessions();"))
        cleaned = result.scalar()
        print(f"✅ CLEANUP function successful (removed {cleaned} expired sessions)")
        
        print("\n🎉 All database operations working correctly!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        db.rollback()
    finally:
        db.close()

def generate_database_module():
    """Generate database.py module for the application"""
    print("\n📝 Generating database.py module...")
    
    database_module = '''"""
Database module for IVA Margem Turismo
Handles PostgreSQL connection and session management
"""
import os
from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()

class Session(Base):
    """Session model for PostgreSQL storage"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_key = Column(String(50), unique=True, index=True, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

class SessionManager:
    """Manages session storage with PostgreSQL backend"""
    
    def __init__(self, db: Optional[DBSession] = None):
        self.db = db
        self.use_database = db is not None
        self.memory_store = {} if not self.use_database else None
    
    def create_session(self, data: Dict[str, Any]) -> str:
        """Create new session and return session key"""
        session_key = str(uuid.uuid4())[:8]
        
        if self.use_database:
            try:
                db_session = Session(
                    session_key=session_key,
                    data=data
                )
                self.db.add(db_session)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise e
        else:
            # Fallback to memory storage
            self.memory_store[session_key] = {
                "data": data,
                "created_at": datetime.utcnow().isoformat()
            }
        
        return session_key
    
    def get_session(self, session_key: str) -> Optional[Dict[str, Any]]:
        """Get session data by key"""
        if self.use_database:
            session = self.db.query(Session).filter(
                Session.session_key == session_key,
                Session.expires_at > datetime.utcnow()
            ).first()
            return session.data if session else None
        else:
            # Fallback to memory storage
            return self.memory_store.get(session_key, {}).get("data")
    
    def update_session(self, session_key: str, data: Dict[str, Any]) -> bool:
        """Update existing session"""
        if self.use_database:
            session = self.db.query(Session).filter_by(session_key=session_key).first()
            if session:
                session.data = data
                session.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
        else:
            # Fallback to memory storage
            if session_key in self.memory_store:
                self.memory_store[session_key]["data"] = data
                return True
            return False
    
    def delete_session(self, session_key: str) -> bool:
        """Delete session"""
        if self.use_database:
            session = self.db.query(Session).filter_by(session_key=session_key).first()
            if session:
                self.db.delete(session)
                self.db.commit()
                return True
            return False
        else:
            # Fallback to memory storage
            if session_key in self.memory_store:
                del self.memory_store[session_key]
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions"""
        if self.use_database:
            result = self.db.execute("SELECT cleanup_expired_sessions();")
            return result.scalar()
        else:
            # Memory storage doesn't have expiration
            return 0

def get_db():
    """Dependency to get database session"""
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

def get_session_manager(db: Optional[DBSession] = None) -> SessionManager:
    """Get session manager instance"""
    return SessionManager(db)
'''
    
    with open("database.py", "w") as f:
        f.write(database_module)
    
    print("✅ database.py module created")

def update_requirements():
    """Update requirements.txt with database dependencies"""
    print("\n📦 Updating requirements.txt...")
    
    new_deps = [
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "redis==5.0.1",
    ]
    
    with open("requirements.txt", "r") as f:
        current_deps = f.read().splitlines()
    
    # Add new dependencies if not present
    updated = False
    for dep in new_deps:
        dep_name = dep.split("==")[0]
        if not any(dep_name in line for line in current_deps):
            current_deps.append(dep)
            updated = True
    
    if updated:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(sorted(current_deps)))
        print("✅ requirements.txt updated with database dependencies")
    else:
        print("ℹ️  requirements.txt already up to date")

def main():
    """Run the migration"""
    if not DATABASE_URL or DATABASE_URL.startswith("postgresql://neondb_owner:neon123"):
        print("\n⚠️  WARNING: Using example DATABASE_URL")
        print("Please set your actual Neon database URL:")
        print("export DATABASE_URL='postgresql://user:pass@host/dbname?sslmode=require'")
        
        response = input("\nContinue with example URL for testing? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Run migration steps
    create_tables()
    create_indexes()
    create_cleanup_function()
    migrate_existing_data()
    test_connection()
    generate_database_module()
    update_requirements()
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Update main.py to import and use database.SessionManager")
    print("2. Set DATABASE_URL environment variable")
    print("3. Deploy to Railway with: railway up")

if __name__ == "__main__":
    main()