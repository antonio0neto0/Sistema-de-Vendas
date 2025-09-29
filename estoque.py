import customtkinter as ctk
from tkinter import ttk, messagebox
import json, os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ARQUIVO_ESTOQUE = "estoque.json"

def centralizar(jan, largura, altura):
    x = (jan.winfo_screenwidth() // 2) - (largura // 2)
    y = (jan.winfo_screenheight() // 2) - (altura // 2)
    jan.geometry(f"{largura}x{altura}+{x}+{y}")

# 🔹 Funções de persistência
def carregar_estoque():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            with open(ARQUIVO_ESTOQUE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_estoque(produtos):
    with open(ARQUIVO_ESTOQUE, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=4, ensure_ascii=False)

def abrir_estoque(menu, callback=None):
    janela = ctk.CTkToplevel(menu)
    janela.title("Sistema de Vendas - Controle de Estoque")
    janela.resizable(True, True)
    centralizar(janela, 800, 500)

    # === Funções internas ===
    def atualizar_ids():
        for i, item in enumerate(tabela.get_children(), start=1):
            valores = tabela.item(item)["values"]
            tabela.item(item, values=(i, *valores[1:]))

    def mostrar_mensagem(texto, cor="red"):
        label_mensagem.configure(text=texto, text_color=cor)
        janela.after(3000, lambda: label_mensagem.configure(text=""))

    def salvar_para_arquivo():
        produtos = []
        for item in tabela.get_children():
            valores = tabela.item(item)["values"]
            produtos.append({
                "id": valores[0],
                "nome": valores[1],
                "quantidade": valores[2],
                "preco": str(valores[3])  # já vem formatado com R$
            })
        salvar_estoque(produtos)

    # === Popups ===
    def adicionar_produto():
        popup = ctk.CTkToplevel(janela)
        popup.title("Adicionar Produto")
        popup.resizable(False, False)
        centralizar(popup, 350, 350)

        label_msg = ctk.CTkLabel(popup, text="", text_color="red", font=("Arial",10))
        label_msg.pack(pady=5)

        ctk.CTkLabel(popup, text="Nome:").pack(pady=(5,0))
        entry_nome = ctk.CTkEntry(popup); entry_nome.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Quantidade:").pack(pady=(5,0))
        entry_quant = ctk.CTkEntry(popup); entry_quant.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Preço:").pack(pady=(5,0))
        entry_preco = ctk.CTkEntry(popup); entry_preco.pack(pady=2, fill="x", padx=20)

        def salvar():
            erros=[]
            nome = entry_nome.get(); quant = entry_quant.get(); preco = entry_preco.get()
            if not nome: erros.append("Nome: obrigatório")
            try: quant = int(quant)
            except: erros.append("Quantidade: deve ser inteiro")
            try: preco = float(preco)
            except: erros.append("Preço: deve ser número")
            if erros:
                label_msg.configure(text="\n".join(erros))
                return
            tabela.insert("", "end", values=(len(tabela.get_children())+1, nome, quant, f"R$ {preco:.2f}"))
            salvar_para_arquivo()
            popup.destroy()

        btn_salvar = ctk.CTkButton(popup, text="Salvar", command=salvar); btn_salvar.pack(pady=10)
        entry_nome.bind("<Return>", lambda e: salvar())
        entry_quant.bind("<Return>", lambda e: salvar())
        entry_preco.bind("<Return>", lambda e: salvar())

    def editar_produto():
        selected = tabela.selection()
        if not selected:
            mostrar_mensagem("Selecione um produto para editar!")
            return
        valores = tabela.item(selected[0])["values"]

        popup = ctk.CTkToplevel(janela)
        popup.title("Editar Produto"); popup.resizable(False, False)
        centralizar(popup, 350, 300)
        label_msg = ctk.CTkLabel(popup, text="", text_color="red", font=("Arial",10)); label_msg.pack(pady=5)

        ctk.CTkLabel(popup, text="Nome:").pack(pady=(5,0))
        entry_nome=ctk.CTkEntry(popup); entry_nome.pack(pady=2, fill="x", padx=20); entry_nome.insert(0,valores[1])
        ctk.CTkLabel(popup, text="Quantidade:").pack(pady=(5,0))
        entry_quant=ctk.CTkEntry(popup); entry_quant.pack(pady=2, fill="x", padx=20); entry_quant.insert(0,valores[2])
        ctk.CTkLabel(popup, text="Preço:").pack(pady=(5,0))
        preco_str = str(valores[3]).replace("R$","").strip()
        entry_preco=ctk.CTkEntry(popup); entry_preco.pack(pady=2, fill="x", padx=20); entry_preco.insert(0,preco_str)

        def salvar():
            erros=[]
            nome=entry_nome.get(); quant=entry_quant.get(); preco=entry_preco.get()
            if not nome: erros.append("Nome: obrigatório")
            try: quant=int(quant)
            except: erros.append("Quantidade: deve ser inteiro")
            try: preco=float(preco)
            except: erros.append("Preço: deve ser número")
            if erros: label_msg.configure(text="\n".join(erros)); return
            tabela.item(selected[0], values=(valores[0], nome, quant, f"R$ {preco:.2f}"))
            salvar_para_arquivo()
            popup.destroy()

        btn_salvar = ctk.CTkButton(popup, text="Salvar", command=salvar); btn_salvar.pack(pady=10)
        entry_nome.bind("<Return>", lambda e: salvar())
        entry_quant.bind("<Return>", lambda e: salvar())
        entry_preco.bind("<Return>", lambda e: salvar())

    def remover_produto():
        selected = tabela.selection()
        if not selected:
            mostrar_mensagem("Selecione um produto!")
            return
        item = tabela.item(selected[0]); nome = item["values"][1]
        if messagebox.askyesno("Confirmação", f"Remover '{nome}'?"):
            tabela.delete(selected[0]); atualizar_ids(); salvar_para_arquivo()
            mostrar_mensagem("Produto removido", "green")

    def voltar():
        janela.destroy()
        menu.deiconify()
        if callback:
            callback()

    # === Frame Título ===
    frame_titulo = ctk.CTkFrame(janela); frame_titulo.pack(fill="x", pady=(20,10), padx=20)
    ctk.CTkLabel(frame_titulo,text="Controle de Estoque", font=("Arial",18,"bold")).pack(pady=10)

    # === Label de Mensagem ===
    label_mensagem = ctk.CTkLabel(janela,text="", font=("Arial",12)); label_mensagem.pack(pady=5)

    # === Tabela ===
    frame_tabela=ctk.CTkFrame(janela, fg_color=None); frame_tabela.pack(fill="both", expand=True, padx=20, pady=10)
    colunas=("id","nome","quantidade","preco")
    tabela=ttk.Treeview(frame_tabela, columns=colunas, show="headings")
    for c in colunas: tabela.heading(c,text=c.capitalize())
    tabela.column("id",width=50,anchor="center"); tabela.column("nome",width=300,anchor="w")
    tabela.column("quantidade",width=100,anchor="center"); tabela.column("preco",width=100,anchor="center")
    scrollbar=ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set); tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 🔹 Atalhos de usabilidade
    tabela.bind("<Double-1>", lambda e: editar_produto())  # duplo clique para editar
    tabela.bind("<Delete>", lambda e: remover_produto())  # tecla Delete para remover

    # === Botões ===
    frame_botoes=ctk.CTkFrame(janela, fg_color=None); frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes,text="Adicionar", command=adicionar_produto,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Editar", command=editar_produto,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Remover", command=remover_produto,width=120).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes,text="Voltar", fg_color="red", command=voltar,width=120).pack(side="left", padx=5)

    # === Carregar dados do arquivo JSON ===
    dados = carregar_estoque()
    if dados:
        for item in dados:
            tabela.insert("", "end", values=(item["id"], item["nome"], item["quantidade"], item["preco"]))
    else:
        # Se não houver arquivo, insere alguns exemplos
        exemplos = [(1,"Camisa Polo",15,"R$ 59.90"),
                    (2,"Calça Jeans",10,"R$ 120.00"),
                    (3,"Tênis Esportivo",8,"R$ 250.00")]
        for item in exemplos:
            tabela.insert("", "end", values=item)
        salvar_para_arquivo()
