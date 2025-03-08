from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services import UserService, DocumentService,QAService
from datetime import timedelta
from models import User

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['POST'])
async def register():
    data = request.get_json()
    response, status_code = await UserService.register_user(data.get('username'), data.get('email'), data.get('password'))
    return jsonify(response), status_code

@routes.route('/login', methods=['POST'])
async def login():
    data = request.get_json()
    user = await UserService.authenticate_user(data.get('email'), data.get('password'))

    if user:
        print(user)
        access_token = create_access_token(identity=user.email)
        return jsonify(access_token=access_token,expires_delta=False), 200

    return jsonify({"msg": "Invalid credentials"}), 401


#document management
@routes.route("/documentupload", methods=["POST"])
@jwt_required()
async def documentupload():
    return await DocumentService.uploadDocument()

@routes.route("/getdocuments", methods=["GET"])
@jwt_required()
async def getdocuments():
    return await DocumentService.getAllDocuments()

@routes.route("/documentdelete", methods=["DELETE"])
@jwt_required()
async def documentdelete():
    return await DocumentService.deleteDocument()




#QA Routes

@routes.route('/askquestion', methods=['POST'])
@jwt_required()
def ask_question():
    """Handles user queries and returns AI-generated responses using stored embeddings."""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return {"error": "User not found"}, 404

    data = request.get_json()
    query = data.get("query", "").strip()
    document_ids = data.get("document_ids", None)  # Optional document filtering
    new_chat = data.get("new_chat", 0)
    if not query:
        return {"error": "Query is required"}, 400

    # Call QA Service to generate response
    response =  QAService.generate_answer(query, user.id, document_ids,new_chat)
    return jsonify(response)