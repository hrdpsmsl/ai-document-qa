from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
import uuid
from extensions import db
from pgvector.sqlalchemy import Vector

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan", lazy="joined")


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    document_path = db.Column(db.Text, nullable=False)
    document_text = db.Column(db.Text)
    uploaded_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    user = relationship("User", back_populates="documents", lazy="joined")
    embeddings = relationship("Embedding", back_populates="document", cascade="all, delete-orphan", lazy="joined")


class Embedding(db.Model):
    __tablename__ = 'embeddings'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = db.Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete="CASCADE"), nullable=False)
    embedding_vector = db.Column(Vector(768), nullable=False)  # ✅ Use pgvector's Vector type
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    document = relationship("Document", back_populates="embeddings", lazy="joined")
