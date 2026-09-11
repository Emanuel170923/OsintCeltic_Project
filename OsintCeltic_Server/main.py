# Arquivo: OsintCeltic_Server/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import time

app = FastAPI()

# Modelo de dados que a API vai receber
class SearchRequest(BaseModel):
    target: str
    mode: str

# Modelo de resposta que a API vai devolver
class SearchResponse(BaseModel):
    status: str
    data: dict

@app.get("/")
def health_check():
    """Endpoint para o UptimeRobot manter o servidor acordado"""
    return {"status": "online", "message": "OsintCeltic API is running!"}

@app.post("/v1/search", response_model=SearchResponse)
async def search_target(request: SearchRequest):
    """Endpoint principal de busca"""
    print(f"[*] Recebendo busca para: {request.target} (Modo: {request.mode})")
    
    # Aqui é onde a lógica de busca pesada (Selenium/Scraping) será chamada
    # Por enquanto, simulamos o tempo de processamento do servidor
    time.sleep(3) 
    
    # Simulação de resposta de dados reais
    mock_data = {
        "full_name": request.target.upper(),
        "cpf": "000.000.000-00",
        "email": "contato@exemplo.com",
        "telefone": "(11) 99999-8888",
        "endereco": "Rua de Exemplo, 123, São Paulo - SP",
        "status": "Dados extraídos com sucesso"
    }
    
    return SearchResponse(status="success", data=mock_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
