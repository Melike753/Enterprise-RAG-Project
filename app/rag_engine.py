import chromadb
import os
import hashlib
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        """
        Vektör veritabanı yönetimini başlatan kurumsal katman.
        """
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        # Mesafe metriği olarak 'cosine' seçildi. 
        self.collection = self.chroma_client.get_or_create_collection(
            name="sirket_rehberi",
            metadata={"hnsw:space": "cosine"}
        )

    def _generate_id(self, text: str):
        """Metinden benzersiz bir ID üretir."""
        return hashlib.md5(text.encode()).hexdigest()

    def index_documents(self):
        """
        Dokümanı anlamsal parçalara ayırır ve vektör veritabanına işler.
        """
        data_path = "data/sirket_bilgileri.txt"
        
        if not os.path.exists(data_path):
            logger.error(f"Hata: {data_path} dosyası bulunamadı.")
            return "Dosya bulunamadı. Lütfen 'data/' klasörünü kontrol edin."

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. Geliştirilmiş Parçalama (Chunking)
            # Sadece satır bazlı değil, boş satırlara göre (paragraf) bölmek anlamsal bütünlüğü korumak için daha sağlıklı.
            raw_chunks = [c.strip() for c in content.split('\n') if len(c.strip()) > 10]
            
            documents = []
            ids = []
            for chunk in raw_chunks:
                doc_id = self._generate_id(chunk)
                documents.append(chunk)
                ids.append(doc_id)

            # 2. Upsert
            if documents:
                self.collection.upsert(
                    documents=documents,
                    ids=ids
                )
                logger.info(f"{len(documents)} parça başarıyla indekslendi.")
                return f"Doküman {len(documents)} anlamlı parçaya bölündü ve kaydedildi."
            
            return "İşlenecek metin bulunamadı."

        except Exception as e:
            logger.error(f"İndeksleme hatası: {str(e)}")
            return f"Hata oluştu: {str(e)}"

    def query_documents(self, user_query: str):
        """
        Kullanıcının sorusuna en yakın döküman parçalarını getirir.
        """
        try:
            # n_results değerini 4 olarak optimize ettim.
            results = self.collection.query(
                query_texts=[user_query],
                n_results=4
            )

            if not results['documents'] or not results['documents'][0]:
                logger.info(f"Sorgu için bağlam bulunamadı: {user_query}")
                return ""

            # Bulunan parçaları birleştirirken her birinin başına numara eklemek modelin (Gemma) bilgileri birbirinden ayırt etmesine yardımcı olur.
            context_parts = []
            for i, doc in enumerate(results['documents'][0], 1):
                context_parts.append(f"Kaynak {i}: {doc}")
            
            context = "\n\n".join(context_parts)
            return context

        except Exception as e:
            logger.error(f"Sorgu hatası: {str(e)}")
            return ""
        