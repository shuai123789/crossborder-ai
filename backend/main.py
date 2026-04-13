from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from typing import List
import os
import requests
import asyncio
import shutil
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Import services
from rag_service import get_rag_service
# from scraper_service import get_scraper_service
from pricing_agent import get_pricing_agent
from models import get_store

app = FastAPI(title="CrossBorder AI API", version="0.1.0")

# Thread pool for sync code
executor = ThreadPoolExecutor(max_workers=2)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://crossborder-ai-seven.vercel.app", "https://crossborder-ai.pages.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== Basic Endpoints ==========

@app.get("/")
async def root():
    return {"message": "CrossBorder AI API running", "version": "0.1.0", "model": "DeepSeek"}


@app.get("/health")
async def health():
    return {"status": "ok"}


# ========== RAG Chat Endpoints ==========

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Search relevant documents
    rag_service = get_rag_service()
    if not rag_service.vector_store:
        rag_service.load_index()

    results = rag_service.search(request.question, top_k=3)

    if not results:
        return ChatResponse(
            answer="Sorry, no relevant information found.",
            sources=[]
        )

    # 2. Build prompt
    context = "\n\n".join([r['content'] for r in results])
    prompt = f"""Based on the following information, answer the question:

{context}

Question: {request.question}

Please answer in Chinese, concise and clear:"""

    # 3. Call DeepSeek API
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a professional cross-border e-commerce customer service assistant"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )

        answer = response.json()['choices'][0]['message']['content']

        return ChatResponse(
            answer=answer,
            sources=[r['source'] for r in results]
        )

    except Exception as e:
        return ChatResponse(
            answer=f"Error generating answer: {str(e)}",
            sources=[]
        )


# ========== Pricing Assistant Endpoints ==========

class PricingRequest(BaseModel):
    url: str


class PricingResponse(BaseModel):
    product_info: dict
    pricing_advice: dict


@app.post("/api/pricing", response_model=PricingResponse)
async def pricing(request: PricingRequest):
    """
    Pricing assistant: input product URL, return competitor info and pricing advice
    """
    try:
        # 1. Scrape competitor info
        loop = asyncio.get_event_loop()
        scraper = get_scraper_service()
        product_info = await loop.run_in_executor(
            executor, 
            scraper.scrape_amazon, 
            request.url
        )

        if 'error' in product_info:
            return PricingResponse(
                product_info=product_info,
                pricing_advice={
                    "error": "Scraping failed",
                    "reasoning": product_info.get('error', 'Unknown error')
                }
            )

        # 2. Agent analysis
        agent = get_pricing_agent()
        pricing_advice = await loop.run_in_executor(
            executor,
            agent.analyze_competitor,
            product_info
        )

        return PricingResponse(
            product_info=product_info,
            pricing_advice=pricing_advice
        )

    except Exception as e:
        return PricingResponse(
            product_info={"url": request.url},
            pricing_advice={
                "error": str(e),
                "strategy": "Analysis failed"
            }
        )


# ========== Data Persistence ==========

@app.post("/api/save")
async def save_product(request: PricingRequest):
    """Save product to tracking list"""
    try:
        loop = asyncio.get_event_loop()
        scraper = get_scraper_service()
        product_info = await loop.run_in_executor(
            executor, 
            scraper.scrape_amazon, 
            request.url
        )
        
        store = get_store()
        record = store.save(product_info)
        
        return {
            "success": True,
            "message": "Saved successfully",
            "data": record
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/products")
async def list_products():
    """Get all tracked products"""
    try:
        store = get_store()
        products = store.get_all()
        return {
            "success": True,
            "count": len(products),
            "data": products
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/products")
async def delete_product(url: str):
    """Delete product record"""
    try:
        store = get_store()
        store.delete(url)
        return {"success": True, "message": "Deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========== Copywriting Endpoints ==========

from copywriting_service import get_copywriting_service, CopywritingResult


class CopywritingRequest(BaseModel):
    product_name: str
    key_points: List[str]
    keywords: List[str]
    platform: str = "amazon"
    language: str = "en"
    tone: str = "professional"


class CopywritingResponse(BaseModel):
    title: str
    description: str
    bullet_points: List[str]
    hashtags: List[str]
    seo_keywords: List[str]
    platform: str
    language: str


@app.post("/api/copywriting", response_model=CopywritingResponse)
async def generate_copywriting(request: CopywritingRequest):
    """AI generate product copywriting"""
    try:
        service = get_copywriting_service()
        result = service.generate(
            product_name=request.product_name,
            key_points=request.key_points,
            keywords=request.keywords,
            platform=request.platform,
            language=request.language,
            tone=request.tone
        )

        return CopywritingResponse(
            title=result.title,
            description=result.description,
            bullet_points=result.bullet_points,
            hashtags=result.hashtags,
            seo_keywords=result.seo_keywords,
            platform=result.platform,
            language=result.language
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== Knowledge Base Management ==========

KNOWLEDGE_DIR = Path(__file__).parent / "data" / "knowledge"

@app.post("/api/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...)):
    """Upload knowledge base document"""
    try:
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        
        file_path = KNOWLEDGE_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        return {
            "success": True,
            "message": f"File {file.filename} uploaded successfully",
            "filename": file.filename
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/knowledge/files")
async def list_knowledge_files():
    """Get knowledge base file list"""
    try:
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        files = []
        for f in KNOWLEDGE_DIR.glob("*.txt"):
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime
            })
        return {
            "success": True,
            "count": len(files),
            "files": files
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.delete("/api/knowledge/files/{filename}")
async def delete_knowledge_file(filename: str):
    """Delete knowledge base file"""
    try:
        file_path = KNOWLEDGE_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return {"success": True, "message": f"{filename} deleted"}
        else:
            return {"success": False, "error": "File not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/knowledge/build-index")
async def build_knowledge_index():
    """Rebuild knowledge base index"""
    try:
        rag_service = get_rag_service()
        success = rag_service.build_index()
        if success:
            return {"success": True, "message": "Knowledge base index built successfully"}
        else:
            return {"success": False, "error": "No documents to index"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ========== Multi-Agent Pricing Analysis API ==========

from multi_agent_system import AgentOrchestrator

class MultiAgentRequest(BaseModel):
    query: str


class MultiAgentResponse(BaseModel):
    success: bool
    plan: dict
    final_report: str
    execution_time: float


@app.post("/api/multi-agent/analyze")
async def multi_agent_analyze(request: MultiAgentRequest):
    """
    Multi-Agent 定价分析接口
    使用 Planner → Retriever → Calculator → Generator → Checker 多 Agent 协作
    """
    import time
    start_time = time.time()
    
    try:
        orchestrator = AgentOrchestrator()
        result = orchestrator.execute(request.query)
        
        execution_time = time.time() - start_time
        
        if result["success"]:
            return {
                "success": True,
                "plan": result["plan"],
                "final_report": result["final_report"],
                "execution_time": round(execution_time, 2)
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "execution_time": round(execution_time, 2)
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "execution_time": round(time.time() - start_time, 2)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
