import customtkinter as ctk
import bcrypt
import json
import os

USUARIO = "neto"
SENHA_HASH = b"$2b$12$HeOnFUIRMvONG99ADgtt8e7LhISPQERGm8M0lJiUy2gwOMoT6z0o2"
ARQUIVO_USUARIO = "usuario.json"

def abrir_login(menu, callback_login_sucesso):
    """
    Cria a janela de login como Toplevel modal do menu.
    callback_login_sucesso: função a chamar quando o login for bem-sucedido
    """
    login_win = ctk.CTkToplevel(menu)
    login_win.title("Sistema de Vendas - Login")
    login_win.geometry("400x300")
    login_win.resizable(False, False)
    login_win.grab_set()  # deixa modal

    # Fecha tudo se o usuário clicar no X
    login_win.protocol("WM_DELETE_WINDOW", menu.destroy)

    def mostrar_mensagem(texto, cor="red"):
        label_mensagem.configure(text=texto, text_color=cor)
        login_win.after(3000, lambda: label_mensagem.configure(text=""))

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
            login_win.destroy()
            callback_login_sucesso()  # mostra o menu
        else:
            mostrar_mensagem("Usuário ou senha incorretos!", "red")
            entry_senha.delete(0, "end")

    # === Elementos da Janela ===
    ctk.CTkLabel(login_win, text="Loja Dessendre", font=("Arial", 20, "bold")).pack(pady=20)

    frame_usuario = ctk.CTkFrame(login_win, fg_color=None, height=35)
    frame_usuario.pack(pady=3, padx=20, fill="x")
    ctk.CTkLabel(frame_usuario, text="Usuário:", width=70, anchor="w").pack(side="left", padx=(0,5))
    entry_usuario = ctk.CTkEntry(frame_usuario, placeholder_text="Digite seu usuário")
    entry_usuario.pack(side="left", fill="x", expand=True)

    frame_senha = ctk.CTkFrame(login_win, fg_color=None, height=35)
    frame_senha.pack(pady=3, padx=20, fill="x")
    ctk.CTkLabel(frame_senha, text="Senha:", width=70, anchor="w").pack(side="left", padx=(0,5))
    entry_senha = ctk.CTkEntry(frame_senha, placeholder_text="Digite sua senha", show="*")
    entry_senha.pack(side="left", fill="x", expand=True)
    entry_senha.bind("<Return>", lambda e: login())

    lembrar_var = ctk.BooleanVar()
    ctk.CTkCheckBox(login_win, text="Lembrar usuário", variable=lembrar_var).pack(pady=5)

    frame_botoes = ctk.CTkFrame(login_win, fg_color=None)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Entrar", command=login, width=100).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Sair", command=menu.destroy, fg_color="red", width=100).pack(side="left", padx=5)

    label_mensagem = ctk.CTkLabel(login_win, text="", font=("Arial", 12))
    label_mensagem.pack(pady=5)

    # Carregar usuário salvo
    if os.path.exists(ARQUIVO_USUARIO):
        with open(ARQUIVO_USUARIO, "r") as f:
            dados = json.load(f)
            entry_usuario.insert(0, dados.get("usuario", ""))
            lembrar_var.set(True)
