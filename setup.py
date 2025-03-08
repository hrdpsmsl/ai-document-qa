# Add these at the top of your settings.py
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)


def enable_pgvector(conn):
    cur = conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    cur.close()
    print("pgvector extension enabled.")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection to neontech PostgreSQL successful!")

    # Create a cursor to execute queries
    cursor = conn.cursor()
    enable_pgvector(conn)

    # Check if the tables exist or create them
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            document_name VARCHAR(255) NOT NULL,
            document_path TEXT NOT NULL,
            document_text TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
            embedding_vector VECTOR(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Commit the changes
    conn.commit()

    # Close cursor and connection
    cursor.close()
    conn.close()

    print("Tables checked/created successfully!")

except Exception as error:
    print("Error connecting to the database:", error)




# CREATE TABLE IF NOT EXISTS documents (
#             id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#             user_id UUID REFERENCES users(id) ON DELETE CASCADE,
#             document_name VARCHAR(255) NOT NULL,
#             document_path TEXT NOT NULL,
#             uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );