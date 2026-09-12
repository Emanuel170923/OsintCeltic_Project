import customtkinter as ctk
from tkinter import messagebox
import threading
import requests  # Essencial para falar com a API
import time

# Configurações de Estilo
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OsintCelticClient(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURAÇÃO CRUCIAL ---
        # COLOQUE AQUI A URL QUE O RENDER TE DEU
        self.API_URL = "https://osintceltic-project-1.onrender.com" 

        self.title("OsintCeltic - Intelligence Client")
        self.geometry("1000x700")

        # Layout de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="OSINT\nCELTIC", 
                                      font=ctk.CTkFont(size=28, weight="bold"))
        self.logo_label.pack(pady=(40, 30), padx=10)

        self.btn_search_name = ctk.CTkButton(self.sidebar, text="BUSCA POR NOME", 
                                            command=lambda: self.set_mode("Nome"))
        self.btn_search_name.pack(pady=10, padx=20, fill="x")

        self.btn_search_cpf = ctk.CTkButton(self.sidebar, text="BUSCA POR CPF", 
                                           command=lambda: self.set_mode("CPF"))
        self.btn_search_cpf.pack(pady=10, padx=20, fill="x")

        self.status_label = ctk.CTkLabel(self.sidebar, text="MODO: NOME", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="bottom", pady=20)
        self.mode = "Nome"

        # --- MAIN PANEL ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.main_frame, text="OSINTCELTIC", 
                                       font=ctk.CTkFont(size=45, weight="bold"))
        self.title_label.pack(pady=(30, 5))
        
        self.subtitle_label = ctk.CTkLabel(self.main_frame, text="Remote Intelligence Connection", 
                                          font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 20))

        self.input_field = ctk.CTkEntry(self.main_frame, placeholder_text="Digite o Alvo...", 
                                       width=450, height=45, font=ctk.CTkFont(size=14))
        self.input_field.pack(pady=10)

        self.btn_execute = ctk.CTkButton(self.main_frame, text="INICIAR CONSULTA REMOTA", 
                                        width=200, height=45, font=ctk.CTkFont(size=15, weight="bold"),
                                        fg_color="#e74c3c", hover_color="#c0392b",
                                        command=self.start_search_thread)
        self.btn_execute.pack(pady=20)

        self.result_text = ctk.CTkTextbox(self.main_frame, width=600, height=300, 
                                         font=ctk.CTkFont(family="Consolas", size=13))
        self.result_text.pack(pady=10, padx=30, fill="both", expand=True)
        self.result_text.insert("0.0", "[!] Cliente Conectado. Aguardando comando...\n")

    def set_mode(self, mode):
        self.mode = mode
        self.status_label.configure(text=f"MODO: {mode.upper()}")
        self.input_field.configure(placeholder_text="Digite o Nome Completo..." if mode == "Nome" else "Digite o CPF...")

    def start_search_thread(self):
        query = self.input_field.get().strip()
        if not query:
            messagebox.showwarning("Aviso", "Insira um alvo!")
            return

        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", f"[!] SOLICITANDO DADOS AO SERVIDOR...\n")
        self.result_text.insert("end", f"[*] Alvo: {query.upper()}\n")
        self.result_text.insert("end", "[*] Conectando à API no Render...\n")
        
        # Inicia a chamada de API em uma thread para não travar a interface
        threading.Thread(target=self.call_api, args=(query,), daemon=True).start()

    def call_api(self, target):
        """Faz a requisição real para o seu servidor remoto"""
        payload = {
            "target": target,
            "mode": self.mode
        }
        
        try:
            # Aumentamos o timeout para 60 segundos para dar tempo do servidor processar
            response = requests.post(self.API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                self.display_results(data)
            else:
                self.result_text.insert("end", f"\n[!] ERRO NO SERVIDOR: {response.status_code}\n")
                self.result_text.insert("end", f"[*] Resposta: {response.text}\n")

        except Exception as e:
            self.result_text.insert("end", f"\n[!] ERRO DE CONEXÃO: {str(e)}\n")
            self.result_text.insert("end", "[!] Verifique se a URL da API está correta e se o servidor está online.\n")

    def display_results(self, data):
        """Exibe os dados que vieram da API no terminal do cliente"""
        self.result_text.insert("end", "\n" + "="*40 + "\n")
        self.result_text.insert("end", "       DADOS RECEBIDOS DA API\n")
        self.result_text.insert("end", "="*40 + "\n")
        
        # Aqui mapeamos os dados que o seu servidor envia no JSON
        self.result_text.insert("end", f"[+] STATUS: {data.get('status', 'OK')}\n")
        self.result_text.insert("end", f"[+] NOME: {data.get('full_name', 'N/A')}\n")
        self.result_text.insert("end", f"[+] CPF: {data.get('cpf', 'N/A')}\n")
        self.result_text.insert("end", f"[+] EMAIL: {data.get('email', 'N/A')}\n")
        self.result_text.insert("end", f"[+] TELEFONE: {data.get('phone', 'N/A')}\n")
        self.result_text.insert("end", f"[+] ENDEREÇO: {data.get('address', 'N/A')}\n")
        
        self.result_text.insert("end", "\n" + "="*40 + "\n")
        self.result_text.insert("end", "[!] Varredura finalizada com sucesso.\n")

if __name__ == "__main__":
    app = OsintCelticClient()
    app.mainloop()
