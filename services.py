import os
import uuid
#import google.generativeai as genai
from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity
from models import User, Document, Embedding
from extensions import db
import bcrypt
from google import genai
from google.genai import types
import pdfplumber
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import base64
import asyncio

qa_bp = Blueprint("qa", __name__)

client = genai.Client(api_key=<gemini-api-key>)
chat_sessions = {}
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # Upload directory

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

######## USER SERVICES
class UserService:
    @staticmethod
    async def register_user(username, email, password):
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return {"msg": "User already exists"}, 400

        # Create user
        new_user = User(username=username, email=email, password_hash=hashed_password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()

        return {"msg": "User created successfully"}, 201

    @staticmethod
    async def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None

######## DOCUMENT SERVICES

class DocumentService:
    @staticmethod
    async def uploadDocument():
        """Handles document upload, stores in DB, and generates embeddings."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {"error": "User not found"}, 404

        if "file" not in request.files:
            return {"error": "No file part"}, 400

        file = request.files["file"]
        if file.filename == "":
            return {"error": "No selected file"}, 400

        # Save file
        file_ext = file.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        
        # Read file content

        def extract_text_from_pdf(file_path):
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()
                return text
            except Exception as e:
                return {"error": f"Error extracting text from PDF: {str(e)}"}, 500
            
        if(file_ext=='pdf'):
            document_content = extract_text_from_pdf(file_path)
            if isinstance(document_content, dict):  # Error response from extract_text_from_pdf
                return document_content
        
        elif(file_ext=='txt'):
            with open(file_path, "r", encoding="utf-8") as f:
                document_content = f.read()
        else:
            return {"error": "Only pdf or txt file is acceptable"}, 400
        try:
            # Generate embedding using the correct method
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=document_content
            )
            if result.embeddings and len(result.embeddings) > 0:
                embedding_vector = result.embeddings[0].values  # Correct extraction
            else:
                return {"error": "Embedding generation failed: No embeddings received"}, 500


            # Store document in DB
            new_document = Document(
                user_id=user.id,
                document_name=file.filename,
                document_path=file_path,
                document_text=document_content
            )
            db.session.add(new_document)
            db.session.commit()

            # Store embedding in DB
            new_embedding = Embedding(
                document_id=new_document.id,
                embedding_vector=embedding_vector
            )
            db.session.add(new_embedding)
            db.session.commit()
            return {"message": "Document uploaded successfully!"}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": f"Embedding generation failed: {str(e)}"}, 500



    @staticmethod
    async def getAllDocuments():
        """Lists all uploaded documents for the authenticated user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {"error": "User not found"}, 404

        documents = Document.query.filter_by(user_id=user.id).all()
        document_list = [
            {
                "id": str(doc.id),
                "document_name": doc.document_name,
                "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for doc in documents
        ]

        return {"documents": document_list}, 200

    @staticmethod
    async def deleteDocument():
        """Deletes a document (and associated embeddings) for the authenticated user."""
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return {"error": "User not found"}, 404

        data = request.get_json()
        document_id = data.get("document_id")

        document = Document.query.filter_by(id=document_id, user_id=user.id).first()
        if not document:
            return {"error": "Document not found"}, 404

        # Delete the document file from storage
        if os.path.exists(document.document_path):
            os.remove(document.document_path)

        # Delete document and associated embeddings from DB
        db.session.delete(document)
        db.session.commit()

        return {"msg": "Document deleted successfully"}, 200



######## QA SERVICES



class QAService:
    @staticmethod
    def get_relevant_documents(query, user_id, document_ids=None):
        """
        Retrieves relevant document embeddings based on cosine similarity to the query embedding.
        Filters based on selected document IDs or all user-uploaded documents.
        """
        # Fetch embeddings based on selected document IDs or all user-uploaded documents
        if document_ids:
            embeddings = Embedding.query.filter(Embedding.document_id.in_(document_ids)).all()
        else:
            user_documents = Document.query.filter_by(user_id=user_id).all()
            doc_ids = [doc.id for doc in user_documents]
            embeddings = Embedding.query.filter(Embedding.document_id.in_(doc_ids)).all()

        if not embeddings:
            return {"error": "No embeddings found"}, 404

        try:
            # Generate embedding for the user query using Gemini API
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=query
            )
            query_embedding = np.array(result.embeddings[0].values).reshape(1, -1)
        except Exception as e:
            return {"error": f"Embedding generation failed: {str(e)}"}, 500

        # Compare query embedding with stored embeddings using cosine similarity
        document_similarities = []
        for embedding in embeddings:
            doc_embedding = np.array(embedding.embedding_vector).reshape(1, -1)
            similarity = cosine_similarity(query_embedding, doc_embedding)
            document_similarities.append((embedding.document, similarity[0][0]))

        # Sort by similarity score (highest first)
        document_similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top 3 relevant documents
        top_documents = [doc[0] for doc in document_similarities[:3]]
        return top_documents
    
    @staticmethod
    def generate_answer(query, user_id, document_ids=None, new_chat=0):
        """
        Retrieves relevant documents and generates an answer using Gemini API in a conversational format.
        """
        
        relevant_documents = QAService.get_relevant_documents(query, user_id, document_ids)
        
        if "error" in relevant_documents:
            return relevant_documents  # If error occurs, return it

        
        # Extract relevant content from the top documents
        context = "\n\n".join([f"{doc.document_name}: {doc.document_text}" for doc in relevant_documents])
       
        
        user_chat_key = str(user_id)  # Using user ID as the key for chat sessions
        print(chat_sessions)
        if new_chat == 1 or user_chat_key not in chat_sessions:
            chat_sessions[user_chat_key] = client.chats.create(model="gemini-1.5-flash")

        chat = chat_sessions[user_chat_key]  # Retrieve chat instance

        # Construct a conversational message format
        messages = [
            {"role": "system", "content": "You are an AI assistant providing answers based on uploaded documents.'"},
            {"role": "user", "content": query},
            {"role": "assistant", "content": f"Relevant information:\n{context}"}  # Provide document context
        ]
        try:
            if(new_chat==1):
                chat = client.chats.create(model='gemini-1.5-flash')
            response = chat.send_message(message="\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages]))
            return {"response": response.text}, 200
        except Exception as e:
            return {"error": f"Answer generation failed: {str(e)}"}, 500
