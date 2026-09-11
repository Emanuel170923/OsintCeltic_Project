import os
import subprocess
import sys

def run_command(command):
    print(f"[*] Executando: {command}")
    process = subprocess.Popen(command, shell=True)
    process.wait()

def setup_environment():
    print("\n" + "="*50)
    print("      OSINTCELTIC - SYSTEM PROVISIONING")
    print("="*50)

    # 1. Criar Ambiente Virtual (venv)
    print("\n[1/3] Criando ambiente virtual isolado (venv)...")
    run_command(f"{sys.executable} -m venv venv")

    # 2. Caminhos do venv (Windows vs Linux/Kali)
    if os.name == 'nt':
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")

    # 3. Atualizar PIP e instalar dependências
    print("\n[2/3] Atualizando PIP e instalando dependências essenciais...")
    run_command(f"{pip_path} install --upgrade pip setuptools wheel")
    
    print("\n[3/3] Instalando dependências do projeto (isso pode demorar)...")
    if os.path.exists("requirements.txt"):
        run_command(f"{pip_path} install -r requirements.txt")
    else:
        print("[!] Erro: requirements.txt não encontrado!")
        return

    print("\n" + "="*50)
    print("[+] INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"[+] Para iniciar o OsintCeltic, use: {python_path} main.py")
    print("="*50)

    choice = input("\n[?] Deseja iniciar a aplicação agora? (s/n): ")
    if choice.lower() == 's':
        run_command(f"{python_path} main.py")

if __name__ == "__main__":
    setup_environment()
