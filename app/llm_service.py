import requests
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, model_name="gemma2:9b"):
        """
        Gemma 2 9B gibi yüksek kapasiteli modeller için optimize edilmiş yapılandırıcı.
        """
        self.api_url = "http://localhost:11434/api/generate"
        self.model_name = model_name

    def ask(self, prompt: str):
        """
        Ollama API üzerinden modeli en kararlı ve tutarlı modda çalıştırır.
        """
        # Gemma 2 9B'nin mantık yürütme kapasitesini 'uydurma' yapmadan 
        # kullanabilmesi için optimize edilmiş parametreler.
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,      # Kesinlik için yaratıcılığı sıfırlıyoruz.
                "top_p": 0.1,            # Sadece en yüksek olasılıklı mantıksal kelimeler.
                "num_ctx": 4096,         # Hafıza penceresi (RAG bağlamı için kritik).
                "num_predict": 512,      # Cevabın yeterli uzunlukta olmasını sağlar.
                "repeat_penalty": 1.2    # Modelin kendini tekrar etmesini engeller.
            }
        }
        
        try:
            logger.info(f"LLM isteği gönderiliyor: {self.model_name}")
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status() # HTTP hatalarını (404, 500 vb.) yakalar
            
            result = response.json().get("response", "")
            
            if not result:
                logger.warning("Model boş bir yanıt döndürdü.")
                return "Üzgünüm, bu soruya uygun bir cevap üretemedim."
                
            return result.strip()

        except requests.exceptions.Timeout:
            logger.error("Ollama yanıt vermedi (Timeout).")
            return "Hata: Model yanıt süresi doldu. Lütfen Ollama'nın çalıştığından emin olun."
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            return f"Hata: Yerel servis bağlantı hatası oluştu."
            
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {str(e)}")
            return "Sistemde beklenmeyen bir hata oluştu."
        