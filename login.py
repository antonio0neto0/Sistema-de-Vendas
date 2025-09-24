import customtkinter as ctk
import subprocess
import sys
import bcrypt
import os
import json

# Configurações globais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

USUARIO = "neto"
# hash gerado para a senha "248652"
SENHA_HASH = b"$2b$12$HeOnFUIRMvONG99ADgtt8e7LhISPQERGm8M0lJiUy2gwOMoT6z0o2"

ARQUIVO_USUARIO = "usuario.json"

# ==== FUNÇÕES ====
def login():
    usuario = entry_usuario.get()
    senha = entry_senha.get().encode()

    if usuario == USUARIO and bcrypt.checkpw(senha, SENHA_HASH):
        mostrar_mensagem("Login realizado com sucesso!", "green")
        if lembrar_var.get():
            # salva apenas o nome do usuário
            with open(ARQUIVO_USUARIO, "w") as f:
                json.dump({"usuario": usuario}, f)
        else:
            if os.path.exists(ARQUIVO_USUARIO):
                os.remove(ARQUIVO_USUARIO)
        janela.after(1000, abrir_menu)
    else:
        mostrar_mensagem("Usuário ou senha incorretos!", "red")

def mostrar_mensagem(texto, cor):
    label_mensagem.configure(text=texto, text_color=cor)
    janela.after(3000, lambda: label_mensagem.configure(text=""))

def abrir_menu():
    janela.destroy()
    subprocess.Popen([sys.executable, "menu.py"])

def sair():
    sys.exit()

# ==== JANELA ====
janela = ctk.CTk()
janela.title("Sistema de Vendas - Login")
janela.geometry("400x300")
janela.resizable(False, False)

janela.iconbitmap("imagens/login.ico")
# ==== ELEMENTOS ====  
label_titulo = ctk.CTkLabel(janela, text="Loja Dessendre", font=("Arial", 20, "bold"))
label_titulo.pack(pady=20)

# ---- Frame Usuário ----
frame_usuario = ctk.CTkFrame(janela, fg_color=None, height=35)
frame_usuario.pack(pady=3, padx=20, fill="x")

label_usuario = ctk.CTkLabel(frame_usuario, text="Usuário:", width=70, anchor="w")
label_usuario.pack(side="left", padx=(0,5))

entry_usuario = ctk.CTkEntry(frame_usuario, placeholder_text="Digite seu usuário")
entry_usuario.pack(side="left", fill="x", expand=True)

# ---- Frame Senha ----
frame_senha = ctk.CTkFrame(janela, fg_color=None, height=35)
frame_senha.pack(pady=3, padx=20, fill="x")

label_senha = ctk.CTkLabel(frame_senha, text="Senha:", width=70, anchor="w")
label_senha.pack(side="left", padx=(0,5))

entry_senha = ctk.CTkEntry(frame_senha, placeholder_text="Digite sua senha", show="*")
entry_senha.pack(side="left", fill="x", expand=True)

# ---- Checkbox lembrar usuário ----
lembrar_var = ctk.BooleanVar()
check_lembrar = ctk.CTkCheckBox(janela, text="Lembrar usuário", variable=lembrar_var)
check_lembrar.pack(pady=5)

# ==== BOTÕES LADO A LADO ====
frame_botoes = ctk.CTkFrame(janela, fg_color=None)
frame_botoes.pack(pady=10)

btn_login = ctk.CTkButton(frame_botoes, text="Entrar", command=login, width=100)
btn_login.pack(side="left", padx=5)

btn_sair = ctk.CTkButton(frame_botoes, text="Sair", command=sair, fg_color="red", width=100)
btn_sair.pack(side="left", padx=5)

# ==== Label de mensagem ====
label_mensagem = ctk.CTkLabel(janela, text="", font=("Arial", 12))
label_mensagem.pack(pady=5)

# ==== CARREGAR USUÁRIO SALVO (SEM SENHA) ====
if os.path.exists(ARQUIVO_USUARIO):
    with open(ARQUIVO_USUARIO, "r") as f:
        dados = json.load(f)
        entry_usuario.insert(0, dados.get("usuario", ""))
        lembrar_var.set(True)

janela.mainloop()
