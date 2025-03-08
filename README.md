# **AI-Powered Document Management & Q&A System**

This application allows users to **register, upload documents, generate embeddings, and perform Q&A** with those documents using **AI-based techniques**. It uses **Flask, PostgreSQL, and Gemini AI** for embedding generation and question-answering while maintaining **conversation history** for contextual interactions.

## **Features**  
✅ User authentication with **JWT**  
✅ Upload and store documents in **PostgreSQL**  
✅ Generate embeddings using **Gemini AI**  
✅ Query documents with **AI-powered retrieval**  
✅ Maintain **conversation history** for contextual responses  
✅ **Containerized** using Docker & Docker Compose  
✅ Automated **CI/CD** with GitHub Actions  

---

## **1️⃣ Prerequisites**  
Ensure you have the following installed:  

- **Python 3.10+**  
- **PostgreSQL (with `vector` extension enabled)**  
- **Docker & Docker Compose**  
- **GitHub CLI (for CI/CD setup, optional)**  

---

## **2️⃣ Setup Instructions**  

### **🔹 Step 1: Clone the Repository**  
```bash
git clone https://github.com/your-repo.git
cd your-repo
```

### **🔹 Step 2: Set Up the Environment Variables**  

Create a `.env` file and configure it as follows:  
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## **3️⃣ Running the Application**  

### **▶️ Option 1: Run with Docker**  
```bash
docker-compose up --build
```
Access the application at `http://localhost:8000/`

### **▶️ Option 2: Run Manually**  

#### **Install dependencies**  
```bash
pip install -r requirements.txt
```

#### **Run PostgreSQL DB Setup**  
```bash
python3 setup.py
```

#### **Run Flask Application**  
```bash
python3 app.py
```

---


## **4️⃣ API Endpoints**  

| Method | Endpoint          | Description |
|--------|------------------|-------------|
| POST   | `/register`       | User Registration |
| POST   | `/login`          | User Login |
| POST   | `/documentupload`         | Upload Document |
| GET    | `/getdocuments`      | List Documents |
| DELETE   | `/deletedocument`          | Delete Document |
| POST   | `/askquestion`          | Query AI Q&A |

---

## **5️⃣ Deployment**  
To deploy on a cloud server:  
```bash
docker-compose -f docker-compose.yml up -d
```
Ensure **PostgreSQL** is configured correctly with cloud credentials.

---

💡 **Contributions & Issues**  
Feel free to contribute or raise issues in the **GitHub Issues** section.



