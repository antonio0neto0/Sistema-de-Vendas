import customtkinter as ctk
from tkinter import ttk, messagebox
import json, os, re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ARQUIVO_CLIENTES = "clientes.json"

def centralizar(jan, largura, altura):
    x = (jan.winfo_screenwidth() // 2) - (largura // 2)
    y = (jan.winfo_screenheight() // 2) - (altura // 2)
    jan.geometry(f"{largura}x{altura}+{x}+{y}")

# 🔹 Funções de persistência
def carregar_clientes():
    if os.path.exists(ARQUIVO_CLIENTES):
        try:
            with open(ARQUIVO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_clientes(lista):
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

# 🔹 Função para gerar ID único permanente
def gerar_id_unico():
    dados = carregar_clientes()
    if dados:
        max_id = max(cliente["id"] for cliente in dados)
        return max_id + 1
    return 1

# 🔹 Função para formatar telefone
def formatar_telefone(telefone):
    numeros = re.sub(r"\D", "", telefone)
    if len(numeros) == 10:  # (XX) XXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    elif len(numeros) == 11:  # (XX) XXXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    else:
        return telefone

# 🔹 Função para validar telefone (borda vermelha se inválido)
def validar_telefone(entry):
    numeros = re.sub(r"\D", "", entry.get())
    if len(numeros) not in (10, 11):
        entry.configure(border_color="red")
        return False
    else:
        entry.configure(border_color="gray")
        return True

def abrir_clientes(menu, callback=None):
    janela = ctk.CTkToplevel(menu)
    janela.title("Sistema de Vendas - Cadastro de Clientes")
    janela.resizable(True, True)
    centralizar(janela, 800, 500)

    # === Funções internas ===
    def mostrar_mensagem(texto, cor="red"):
        label_mensagem.configure(text=texto, text_color=cor)
        janela.after(3000, lambda: label_mensagem.configure(text=""))

    def salvar_para_arquivo():
        clientes_lista = []
        for item in tabela.get_children():
            valores = tabela.item(item)["values"]
            clientes_lista.append({
                "id": valores[0],
                "nome": valores[1],
                "telefone": valores[2],
                "email": valores[3]
            })
        salvar_clientes(clientes_lista)

    # === Popups ===
    def popup_cliente(titulo, valores=None, item_id=None):
        popup = ctk.CTkToplevel(janela)
        popup.title(titulo)
        popup.resizable(False, False)
        centralizar(popup, 350, 300)

        label_msg = ctk.CTkLabel(popup, text="", text_color="red", font=("Arial",10))
        label_msg.pack(pady=5)

        ctk.CTkLabel(popup, text="Nome:").pack(pady=(5,0))
        entry_nome = ctk.CTkEntry(popup); entry_nome.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Telefone:").pack(pady=(5,0))
        entry_tel = ctk.CTkEntry(popup); entry_tel.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="E-mail:").pack(pady=(5,0))
        entry_email = ctk.CTkEntry(popup); entry_email.pack(pady=2, fill="x", padx=20)

        # Preencher campos se for edição
        if valores:
            entry_nome.insert(0, valores[1])
            entry_tel.insert(0, valores[2])
            entry_email.insert(0, valores[3])

        # Validação de telefone em tempo real
        entry_tel.bind("<KeyRelease>", lambda e: validar_telefone(entry_tel))

        def salvar():
            erros = []
            nome = entry_nome.get().strip()
            tel = entry_tel.get().strip()
            email = entry_email.get().strip()
            if not nome: erros.append("Nome: obrigatório")
            if not tel: erros.append("Telefone: obrigatório")
            elif not validar_telefone(entry_tel): erros.append("Telefone inválido")
            if not email: erros.append("E-mail: obrigatório")
            if erros:
                label_msg.configure(text="\n".join(erros))
                return
            tel_formatado = formatar_telefone(tel)
            if valores:  # edição
                tabela.item(item_id, values=(valores[0], nome, tel_formatado, email))
            else:  # novo cliente
                novo_id = gerar_id_unico()
                tabela.insert("", "end", values=(novo_id, nome, tel_formatado, email))
            salvar_para_arquivo()
            popup.destroy()

        ctk.CTkButton(popup, text="Salvar", command=salvar).pack(pady=10)
        entry_nome.bind("<Return>", lambda e: salvar())
        entry_tel.bind("<Return>", lambda e: salvar())
        entry_email.bind("<Return>", lambda e: salvar())

    def adicionar_cliente():
        popup_cliente("Adicionar Cliente")

    def editar_cliente():
        selected = tabela.selection()
        if not selected:
            mostrar_mensagem("Selecione um cliente!")
            return
        valores = tabela.item(selected[0])["values"]
        popup_cliente("Editar Cliente", valores, item_id=selected[0])

    def remover_cliente():
        selected = tabela.selection()
        if not selected:
            mostrar_mensagem("Selecione um cliente!")
            return
        item = tabela.item(selected[0]); nome = item["values"][1]
        if messagebox.askyesno("Confirmação", f"Remover '{nome}'?"):
            tabela.delete(selected[0])
            salvar_para_arquivo()
            mostrar_mensagem("Cliente removido", "green")

    def voltar():
        janela.destroy()
        menu.deiconify()
        if callback:
            callback()

    # === Frame Título ===
    frame_titulo = ctk.CTkFrame(janela); frame_titulo.pack(fill="x", pady=(20,10), padx=20)
    ctk.CTkLabel(frame_titulo,text="Cadastro de Clientes", font=("Arial",18,"bold")).pack(pady=10)

    # === Label de Mensagem ===
    label_mensagem = ctk.CTkLabel(janela,text="", font=("Arial",12)); label_mensagem.pack(pady=5)

    # === Tabela ===
    frame_tabela=ctk.CTkFrame(janela, fg_color=None); frame_tabela.pack(fill="both", expand=True, padx=20, pady=10)
    colunas=("id","nome","telefone","email")
    tabela=ttk.Treeview(frame_tabela, columns=colunas, show="headings")
    for c in colunas: tabela.heading(c,text=c.capitalize())
    tabela.column("id",width=50,anchor="center")
    tabela.column("nome",width=200,anchor="w")
    tabela.column("telefone",width=150,anchor="center")
    tabela.column("email",width=250,anchor="w")
    scrollbar=ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set); tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 🔹 Atalhos de usabilidade
    tabela.bind("<Double-1>", lambda e: editar_cliente())
    tabela.bind("<Delete>", lambda e: remover_cliente())

    # === Botões ===
    frame_botoes=ctk.CTkFrame(janela, fg_color=None); frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes,text="Adicionar", command=adicionar_cliente,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Editar", command=editar_cliente,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Remover", command=remover_cliente,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Voltar", fg_color="red", command=voltar,width=120).pack(side="left", padx=5)

    # === Carregar dados do arquivo JSON ou exemplos iniciais ===
    dados = carregar_clientes()
    if dados:
        for item in dados:
            tabela.insert("", "end", values=(item["id"], item["nome"], item["telefone"], item["email"]))
    else:
        exemplos = [(1,"João Silva","(11) 99999-1111","joao@email.com"),
                    (2,"Maria Souza","(21) 98888-2222","maria@email.com")]
        for item in exemplos:
            tabela.insert("", "end", values=item)
        salvar_para_arquivo()
