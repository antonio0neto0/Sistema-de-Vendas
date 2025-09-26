import customtkinter as ctk
import sys
import bcrypt
import os
import json
from menu import abrir_menu  # importa função do menu

# Configurações globais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

USUARIO = "neto"
# hash gerado para a senha "248652"
SENHA_HASH = b"$2b$12$HeOnFUIRMvONG99ADgtt8e7LhISPQERGm8M0lJiUy2gwOMoT6z0o2"
ARQUIVO_USUARIO = "usuario.json"

# ==== Funções ====
def login():
    usuario = entry_usuario.get()
    senha = entry_senha.get().encode()

    if usuario == USUARIO and bcrypt.checkpw(senha, SENHA_HASH):
        mostrar_mensagem("Login realizado com sucesso!", "green")
        if lembrar_var.get():
            with open(ARQUIVO_USUARIO, "w") as f:
                json.dump({"usuario": usuario}, f)
        else:
            if os.path.exists(ARQUIVO_USUARIO):
                os.remove(ARQUIVO_USUARIO)
        janela.after(500, abrir_menu, janela)  # passa a janela do login
    else:
        mostrar_mensagem("Usuário ou senha incorretos!", "red")
        entry_senha.delete(0, "end")

def mostrar_mensagem(texto, cor):
    label_mensagem.configure(text=texto, text_color=cor)
    janela.after(3000, lambda: label_mensagem.configure(text=""))

def sair():
    sys.exit()

# ==== Janela de Login ====
janela = ctk.CTk()
janela.title("Sistema de Vendas - Login")
janela.geometry("400x300")
janela.resizable(False, False)
try:
    janela.iconbitmap("imagens/login.ico")
except:
    pass

# ==== Elementos ====
label_titulo = ctk.CTkLabel(janela, text="Loja Dessendre", font=("Arial", 20, "bold"))
label_titulo.pack(pady=20)

frame_usuario = ctk.CTkFrame(janela, fg_color=None, height=35)
frame_usuario.pack(pady=3, padx=20, fill="x")
label_usuario = ctk.CTkLabel(frame_usuario, text="Usuário:", width=70, anchor="w")
label_usuario.pack(side="left", padx=(0,5))
entry_usuario = ctk.CTkEntry(frame_usuario, placeholder_text="Digite seu usuário")
entry_usuario.pack(side="left", fill="x", expand=True)

frame_senha = ctk.CTkFrame(janela, fg_color=None, height=35)
frame_senha.pack(pady=3, padx=20, fill="x")
label_senha = ctk.CTkLabel(frame_senha, text="Senha:", width=70, anchor="w")
label_senha.pack(side="left", padx=(0,5))
entry_senha = ctk.CTkEntry(frame_senha, placeholder_text="Digite sua senha", show="*")
entry_senha.pack(side="left", fill="x", expand=True)
entry_senha.bind("<Return>", lambda event: login())

lembrar_var = ctk.BooleanVar()
check_lembrar = ctk.CTkCheckBox(janela, text="Lembrar usuário", variable=lembrar_var)
check_lembrar.pack(pady=5)

frame_botoes = ctk.CTkFrame(janela, fg_color=None)
frame_botoes.pack(pady=10)
btn_login = ctk.CTkButton(frame_botoes, text="Entrar", command=login, width=100)
btn_login.pack(side="left", padx=5)
btn_sair = ctk.CTkButton(frame_botoes, text="Sair", command=sair, fg_color="red", width=100)
btn_sair.pack(side="left", padx=5)

label_mensagem = ctk.CTkLabel(janela, text="", font=("Arial", 12))
label_mensagem.pack(pady=5)

# Carregar usuário salvo
if os.path.exists(ARQUIVO_USUARIO):
    with open(ARQUIVO_USUARIO, "r") as f:
        dados = json.load(f)
        entry_usuario.insert(0, dados.get("usuario", ""))
        lembrar_var.set(True)

janela.mainloop()
