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
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def salvar_clientes(lista):
    with open(ARQUIVO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

# 🔹 Função para gerar ID único permanente
def gerar_id_unico():
    dados = carregar_clientes()
    if dados:
        max_id = max(cliente.get("id", 0) for cliente in dados)
        return max_id + 1
    return 1

# 🔹 Funções de formatação e validação
def formatar_telefone(telefone):
    numeros = re.sub(r"\D", "", telefone)
    if len(numeros) == 10:  # (XX) XXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    elif len(numeros) == 11:  # (XX) XXXXX-XXXX
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    else:
        return telefone

def validar_telefone(entry):
    numeros = re.sub(r"\D", "", entry.get())
    if len(numeros) not in (10, 11):
        entry.configure(border_color="red")
        return False
    else:
        entry.configure(border_color="gray")
        return True

def formatar_e_validar_cpf(entry):
    numeros = re.sub(r"\D", "", entry.get())
    
    if len(numeros) > 11:
        numeros = numeros[:11]
    
    if len(numeros) > 9:
        formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    elif len(numeros) > 6:
        formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
    elif len(numeros) > 3:
        formatado = f"{numeros[:3]}.{numeros[3:]}"
    else:
        formatado = numeros
    
    pos_antiga = entry.index(ctk.INSERT)
    entry.delete(0, ctk.END)
    entry.insert(0, formatado)
    
    nova_pos = pos_antiga
    if len(numeros) > 3 and pos_antiga in (4, 5):
        nova_pos += 1
    if len(numeros) > 6 and pos_antiga in (8, 9):
        nova_pos += 1
    if len(numeros) > 9 and pos_antiga in (12, 13):
        nova_pos += 1
    
    entry.icursor(nova_pos)

    if len(numeros) == 11:
        entry.configure(border_color="gray")
        return True
    else:
        entry.configure(border_color="red")
        return False

def abrir_clientes(menu, callback=None):
    janela = ctk.CTkToplevel(menu)
    janela.title("Sistema de Vendas - Cadastro de Clientes")
    janela.resizable(True, True)
    centralizar(janela, 950, 500)

    # === Funções internas ===
    def mostrar_mensagem(texto, cor="red"):
        label_mensagem.configure(text=texto, text_color=cor)
        janela.after(3000, lambda: label_mensagem.configure(text=""))

    def salvar_para_arquivo():
        clientes_lista = []
        for item in tabela.get_children():
            valores = tabela.item(item)["values"]
            cpf_sem_formatacao = re.sub(r"\D", "", valores[2])
            
            clientes_lista.append({
                "id": valores[0],
                "nome": valores[1],
                "cpf": cpf_sem_formatacao,
                "telefone": valores[3],
                "email": valores[4]
            })
        salvar_clientes(clientes_lista)

    # === Popups ===
    def popup_cliente(titulo, valores=None, item_id=None):
        popup = ctk.CTkToplevel(janela)
        popup.title(titulo)
        popup.resizable(False, False)
        centralizar(popup, 350, 400)

        label_msg = ctk.CTkLabel(popup, text="", text_color="red", font=("Arial",10))
        label_msg.pack(pady=5)

        ctk.CTkLabel(popup, text="Nome:").pack(pady=(5,0))
        entry_nome = ctk.CTkEntry(popup); entry_nome.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="CPF:").pack(pady=(5,0))
        entry_cpf = ctk.CTkEntry(popup); entry_cpf.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Telefone:").pack(pady=(5,0))
        entry_tel = ctk.CTkEntry(popup); entry_tel.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="E-mail:").pack(pady=(5,0))
        entry_email = ctk.CTkEntry(popup); entry_email.pack(pady=2, fill="x", padx=20)

        # Preencher campos se for edição
        if valores:
            entry_nome.insert(0, valores[1])
            entry_cpf.insert(0, valores[2])
            entry_tel.insert(0, valores[3])
            entry_email.insert(0, valores[4])

        # Validação de campos em tempo real
        entry_cpf.bind("<KeyRelease>", lambda e: formatar_e_validar_cpf(entry_cpf))
        entry_tel.bind("<KeyRelease>", lambda e: validar_telefone(entry_tel))

        def salvar():
            erros = []
            nome = entry_nome.get().strip()
            cpf_digitado = re.sub(r"\D", "", entry_cpf.get().strip())
            tel = entry_tel.get().strip()
            email = entry_email.get().strip()
            
            # --- VERIFICAÇÃO DE CPF DUPLICADO ---
            dados_existentes = carregar_clientes()
            
            if dados_existentes:
                for cliente in dados_existentes:
                    cpf_existente = cliente.get("cpf", "")
                    
                    # Se for uma edição, ignora a si mesmo na verificação
                    if valores and cliente["id"] == valores[0]:
                        continue
                        
                    if cpf_existente == cpf_digitado:
                        erros.append("Este CPF já está cadastrado.")
                        break

            if not nome: erros.append("Nome: obrigatório")
            if not cpf_digitado or len(cpf_digitado) != 11: erros.append("CPF inválido (11 dígitos)")
            if not tel: erros.append("Telefone: obrigatório")
            elif len(re.sub(r"\D", "", tel)) not in (10, 11): erros.append("Telefone inválido")
            if not email: erros.append("E-mail: obrigatório")
            
            if erros:
                label_msg.configure(text="\n".join(erros))
                return
            
            tel_formatado = formatar_telefone(tel)
            cpf_formatado = f"{cpf_digitado[:3]}.{cpf_digitado[3:6]}.{cpf_digitado[6:9]}-{cpf_digitado[9:11]}"
            
            if valores:  # Edição
                tabela.item(item_id, values=(valores[0], nome, cpf_formatado, tel_formatado, email))
            else:  # Novo cliente
                novo_id = gerar_id_unico()
                tabela.insert("", "end", values=(novo_id, nome, cpf_formatado, tel_formatado, email))
            
            salvar_para_arquivo()
            popup.destroy()

        ctk.CTkButton(popup, text="Salvar", command=salvar).pack(pady=10)
        entry_nome.bind("<Return>", lambda e: salvar())
        entry_cpf.bind("<Return>", lambda e: salvar())
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
    colunas=("id","nome","cpf","telefone","email")
    tabela=ttk.Treeview(frame_tabela, columns=colunas, show="headings")
    for c in colunas: tabela.heading(c,text=c.capitalize())
    tabela.column("id",width=50,anchor="center")
    tabela.column("nome",width=180,anchor="w")
    tabela.column("cpf",width=130,anchor="center")
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
            cpf_exibicao = f"{item['cpf'][:3]}.{item['cpf'][3:6]}.{item['cpf'][6:9]}-{item['cpf'][9:11]}"
            tabela.insert("", "end", values=(item["id"], item["nome"], cpf_exibicao, item["telefone"], item["email"]))
    else:
        exemplos = [(1,"João Silva","11111111111","(11) 99999-1111","joao@email.com"),
                    (2,"Maria Souza","22222222222","(21) 98888-2222","maria@email.com")]
        for item in exemplos:
            # Ao inserir os exemplos, garanta que o CPF seja formatado para exibição
            cpf_exibicao = f"{item[2][:3]}.{item[2][3:6]}.{item[2][6:9]}-{item[2][9:11]}"
            tabela.insert("", "end", values=(item[0], item[1], cpf_exibicao, item[3], item[4]))
        salvar_para_arquivo()