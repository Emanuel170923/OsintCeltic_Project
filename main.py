import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By # Novo: para clicar em elementos
from webdriver_manager.chrome import ChromeDriverManager

# Configurações de Estilo
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OsintCelticApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OsintCeltic - Deep Scraper Engine")
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
        
        self.subtitle_label = ctk.CTkLabel(self.main_frame, text="Deep Web & Public Data Scraper", 
                                          font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 20))

        self.input_field = ctk.CTkEntry(self.main_frame, placeholder_text="Digite o Nome ou CPF...", 
                                       width=450, height=45, font=ctk.CTkFont(size=14))
        self.input_field.pack(pady=10)

        self.btn_execute = ctk.CTkButton(self.main_frame, text="INICIAR BUSCA PROFUNDA", 
                                        width=200, height=45, font=ctk.CTkFont(size=15, weight="bold"),
                                        fg_color="#e74c3c", hover_color="#c0392b",
                                        command=self.start_search_thread)
        self.btn_execute.pack(pady=20)

        self.result_text = ctk.CTkTextbox(self.main_frame, width=600, height=300, 
                                         font=ctk.CTkFont(family="Consolas", size=13))
        self.result_text.pack(pady=10, padx=30, fill="both", expand=True)
        self.result_text.insert("0.0", "[!] Sistema Pronto. Aguardando alvo...\n")

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
        self.result_text.insert("end", f"[!] INICIANDO BUSCA PROFUNDA: {query.upper()}\n")
        self.result_text.insert("end", "[*] Configurando motor de busca...\n")
        
        threading.Thread(target=self.perform_real_search, args=(query,), daemon=True).start()

    def perform_real_search(self, target):
        options = Options()
        options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        driver = None
        try:
            self.result_text.insert("end", "[*] Abrindo navegador...\n")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Dork para buscar sites que contenham o nome e dados sensíveis
            search_query = f'"{target}" endereço telefone OR cpf'
            driver.get(f"https://www.google.com/search?q={search_query}")
            time.sleep(5) # Espera carregar os resultados

            # 1. Pegar os links dos resultados da busca
            self.result_text.insert("end", "[*] Coletando links de resultados...\n")
            links = []
            links_elements = driver.find_elements(By.CSS_SELECTOR, "div.g a") # Seleciona os links dos resultados do Google
            
            for link in links_elements[:3]: # Limita a 3 sites para não demorar muito
                url = link.get_attribute('href')
                if url and "google" not in url:
                    links.append(url)

            if not links:
                self.result_text.insert("end", "[!] Nenhum link relevante encontrado.\n")
            else:
                self.result_text.insert(f"[+] {len(links)} sites encontrados. Iniciando escavação...\n")

            # 2. Entrar em cada site e ler o conteúdo
            for i, url in enumerate(links, 1):
                self.result_text.insert(f"\n[*] Escavando Site {i}: {url[:40]}...\n")
                try:
                    driver.get(url)
                    time.sleep(3) # Espera o site carregar o conteúdo real
                    
                    # Captura o texto de TODA a página
                    page_content = driver.find_element(By.TAG_NAME, "body").text
                    
                    # 3. Tentar extrair dados do texto da página
                    self.extract_data_from_text(page_content, target)
                except Exception as e:
                    self.result_text.insert("end", f"    [!] Erro ao acessar site: {str(e)[:30]}\n")

            self.result_text.insert("end", "\n" + "="*40 + "\n")
            self.result_text.insert("end", "       VARREDURA CONCLUÍDA\n")
            self.result_text.insert("end", "="*40 + "\n")

        except Exception as e:
            self.result_text.insert("end", f"\n[!] ERRO CRÍTICO: {str(e)}\n")
        finally:
            if driver:
                driver.quit()

    def extract_data_from_text(self, text, target):
        """
        Usa REGEX para encontrar padrões reais no texto da página.
        """
        self.result_text.insert("end", "[*] Analisando conteúdo da página...\n")
        
        # Regex para CPF
        cpf_pattern = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
        # Regex para Telefone (vários formatos)
        tel_pattern = re.findall(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', text)
        # Regex para E-mail
        email_pattern = re.findall(r'[\w\.-]+@[\w\.-]+', text)

        if cpf_pattern:
            self.result_text.insert("end", f"    [+] CPF DETECTADO: {cpf_pattern[0]}\n")
        
        if tel_pattern:
            for tel in set(tel_pattern): # set para não repetir
                self.result_text.insert("end", f"    [+] TELEFONE DETECTADO: {tel}\n")

        if email_pattern:
            for email in set(email_pattern):
                self.result_text.insert("end", f"    [+] EMAIL DETECTADO: {email}\n")

        if not cpf_pattern and not tel_pattern and not email_pattern:
            self.result_text.insert("end", "    [?] Nenhum dado sensível detectado nesta página.\n")

        self.result_text.insert("end", "-"*30 + "\n")

if __name__ == "__main__":
    app = OsintCelticApp()
    app.mainloop()
