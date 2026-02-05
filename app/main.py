from fastapi import FastAPI, HTTPException, Query
from app.llm_service import LLMService
from app.rag_engine import RAGEngine
import time

# API Tanımlaması
app = FastAPI(
    title="Y İnovasyon Kurumsal RAG API",
    description="Hız için optimize edilmiş, yerel LLM tabanlı döküman soru-cevap sistemi.",
    version="2.1.1"
)

# Servisleri başlatıyoruz
llm = LLMService()
rag = RAGEngine()

@app.get("/health", tags=["Sistem"])
def health_check():
    return {
        "status": "active",
        "model": llm.model_name,
        "message": "Y İnovasyon Yapay Zeka Servisi optimize edilmiş modda çalışıyor."
    }

@app.get("/index", tags=["Veri Yönetimi"])
def index_docs():
    try:
        message = rag.index_documents()
        return {"status": "success", "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"İndeksleme sırasında hata: {str(e)}")

@app.get("/ask", tags=["Soru-Cevap"])
def ask_question(
    query: str = Query(None, description="Sormak istediğiniz soru", min_length=3)
):
    """
    Doğrudan RAG akışı ile hızlı cevap üretir.
    """
    # 1. Giriş Doğrulama
    if not query or query.strip() == "":
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir soru giriniz.")

    start_time = time.time()

    context = rag.query_documents(query)
    
    # 3. Guardrail Prompt (Sistem Talimatı)
    system_instruction = (
        "### GÖREV ###\n"
        "Sen Y İnovasyon şirketinin resmi asistanısın. Aşağıdaki BİLGİ kısmını kullanarak SORU'ya cevap ver.\n"
        "Kullanıcı bazen devrik veya günlük ifadeler kullanabilir, dökümandaki anlamla eşleştirme yap.\n\n"
        "### KESİN KURALLAR ###\n"
        "1. Sadece sana verilen BİLGİ kısmına sadık kal. Bilgi yoksa uydurma.\n"
        "2. Eğer cevap BİLGİ kısmında geçmiyorsa, doğrudan şunu söyle: 'Üzgünüm, bu konu hakkında dökümanlarda bilgi bulamadım.'\n"
        "3. Cevabın profesyonel ve kısa olsun.\n"
        "4. 'Soru:', 'Cevap:' gibi başlıkları tekrar etme.\n"
    )
    
    # RAG Bağlamı kurgusu
    if context:
        prompt = f"{system_instruction}\nBİLGİ:\n{context}\n\nSORU: {query}\n\nCEVAP:"
    else:
        prompt = f"{system_instruction}\nBİLGİ:\n(Bilgi bulunamadı)\n\nSORU: {query}\n\nCEVAP:"

    # 4. Generation (Cevap Üretimi)
    response = llm.ask(prompt)
    processing_time = round(time.time() - start_time, 2)

    return {
        "query": query,
        "response": response,
        "metadata": {
            "context_found": True if context else False,
            "processing_time_sec": processing_time,
            "engine": llm.model_name
        }
    }
