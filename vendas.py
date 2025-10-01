import customtkinter as ctk
from tkinter import ttk, messagebox
import json, os, re
from datetime import datetime
import estoque
import clientes

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ARQUIVO_VENDAS = "vendas.json"

def centralizar(jan, largura, altura):
    x = (jan.winfo_screenwidth() // 2) - (largura // 2)
    y = (jan.winfo_screenheight() // 2) - (altura // 2)
    jan.geometry(f"{largura}x{altura}+{x}+{y}")

def salvar_venda(venda):
    vendas = []
    if os.path.exists(ARQUIVO_VENDAS):
        with open(ARQUIVO_VENDAS, "r", encoding="utf-8") as f:
            try:
                vendas = json.load(f)
            except json.JSONDecodeError:
                vendas = []
    
    vendas.append(venda)
    
    with open(ARQUIVO_VENDAS, "w", encoding="utf-8") as f:
        json.dump(vendas, f, indent=4, ensure_ascii=False)

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
    
def abrir_vendas(menu, callback=None):
    janela = ctk.CTkToplevel(menu)
    janela.title("Sistema de Vendas - Nova Venda")
    janela.resizable(True, True)
    janela.state("zoomed")
    
    lista_produtos = estoque.carregar_estoque()
    total_bruto_var = ctk.StringVar(value="0.00")
    desconto_var = ctk.StringVar(value="0.00")
    total_final_var = ctk.StringVar(value="0.00")
    
    cliente_selecionado = {"id": None, "nome": "Cliente Não Identificado"}
    cliente_label_var = ctk.StringVar(value="Cliente: Não Identificado")

    def atualizar_totais():
        total_bruto = 0.0
        for item_id in carrinho_tabela.get_children():
            subtotal_str = carrinho_tabela.item(item_id)["values"][4].replace("R$ ","")
            try:
                total_bruto += float(subtotal_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Erro de Cálculo", f"Valor inválido encontrado: {subtotal_str}. Verifique os preços.")
                return
        
        total_bruto_var.set(f"{total_bruto:.2f}")

        desconto_valor = 0.0
        try:
            valor_digitado = float(desconto_entry.get().replace(',', '.') or 0)
            tipo_desconto = desconto_combo.get()
            
            if tipo_desconto == "%":
                desconto_valor = total_bruto * (valor_digitado / 100)
            else:
                desconto_valor = valor_digitado

        except ValueError:
            messagebox.showwarning("Formato de Desconto", "O valor do desconto deve ser um número.")
            desconto_entry.delete(0, "end")
            desconto_entry.insert(0, "0.00")
            desconto_valor = 0
        
        total_final = total_bruto - desconto_valor
        
        desconto_var.set(f"{desconto_valor:.2f}")
        total_final_var.set(f"{total_final:.2f}")

    def adicionar_ao_carrinho(produto, quantidade_adicionar):
        if quantidade_adicionar <= 0:
            messagebox.showwarning("Atenção", "A quantidade deve ser maior que zero.")
            return
        
        qtd_em_estoque = int(produto.get("quantidade", 0))
        
        for item_id in carrinho_tabela.get_children():
            item_valores = carrinho_tabela.item(item_id)["values"]
            if str(item_valores[0]) == str(produto["id"]):
                qtd_no_carrinho = item_valores[2]
                if "temp_" not in str(produto["id"]):
                    if qtd_no_carrinho + quantidade_adicionar > qtd_em_estoque:
                        messagebox.showwarning("Estoque Insuficiente", f"Apenas {qtd_em_estoque} unidades de '{produto['nome']}' em estoque. Você já tem {qtd_no_carrinho} no carrinho.")
                        return
                
                nova_quantidade = qtd_no_carrinho + quantidade_adicionar
                novo_subtotal = nova_quantidade * float(produto["preco"].replace("R$ ","").replace(',', '.'))
                carrinho_tabela.item(item_id, values=(
                    produto["id"],
                    produto["nome"],
                    nova_quantidade,
                    produto["preco"],
                    f"R$ {novo_subtotal:.2f}"
                ))
                atualizar_totais()
                return

        if "temp_" not in str(produto["id"]):
            if quantidade_adicionar > qtd_em_estoque:
                messagebox.showwarning("Estoque Insuficiente", f"Apenas {qtd_em_estoque} unidades de '{produto['nome']}' em estoque. Não é possível adicionar {quantidade_adicionar}.")
                return
            
        subtotal = quantidade_adicionar * float(produto["preco"].replace("R$ ","").replace(',', '.'))
        carrinho_tabela.insert("", "end", values=(
            produto["id"],
            produto["nome"],
            quantidade_adicionar,
            produto["preco"],
            f"R$ {subtotal:.2f}"
        ))
        atualizar_totais()

    def remover_do_carrinho():
        selected = carrinho_tabela.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para remover.")
            return
        
        carrinho_tabela.delete(selected[0])
        messagebox.showinfo("Sucesso", "Item removido do carrinho.")
        atualizar_totais()

    def finalizar_venda():
        if not carrinho_tabela.get_children():
            messagebox.showwarning("Atenção", "O carrinho de compras está vazio!")
            return
        abrir_popup_pagamento()

    def abrir_popup_pagamento(forma_pagamento_pre_selecionada=None):
        if not carrinho_tabela.get_children():
            messagebox.showwarning("Atenção", "O carrinho está vazio.")
            return

        popup = ctk.CTkToplevel(janela)
        popup.title("Pagamento")
        popup.resizable(False, False)
        centralizar(popup, 350, 350)
        
        total_pago = float(total_final_var.get().replace(",", "."))
        label_total = ctk.CTkLabel(popup, text=f"Total a Pagar: R$ {total_pago:.2f}", font=("Arial", 16, "bold"))
        label_total.pack(pady=20)
        
        def combobox_changed(choice):
            if choice == "Dinheiro":
                valor_recebido_entry.delete(0, "end")
            else:
                valor_recebido_entry.delete(0, "end")
                valor_recebido_entry.insert(0, f"{total_pago:.2f}".replace('.',','))
            calcular_troco()
        
        ctk.CTkLabel(popup, text="Forma de Pagamento:").pack(pady=(5,0))
        forma_pagamento_combo = ctk.CTkComboBox(popup, values=["", "Dinheiro", "Cartão de Crédito", "Pix", "Cartão de Débito"], width=200, state="readonly", command=combobox_changed)
        forma_pagamento_combo.pack(pady=5)
        
        if forma_pagamento_pre_selecionada:
            forma_pagamento_combo.set(forma_pagamento_pre_selecionada)
            combobox_changed(forma_pagamento_pre_selecionada)
        
        ctk.CTkLabel(popup, text="Valor Recebido (Dinheiro):").pack(pady=(5,0))
        valor_recebido_entry = ctk.CTkEntry(popup, width=200, placeholder_text="0.00")
        valor_recebido_entry.pack(pady=5)
        
        label_troco = ctk.CTkLabel(popup, text="Troco: R$ 0.00", font=("Arial", 14, "bold"), text_color="green")
        label_troco.pack(pady=10)
        
        valor_recebido_entry.focus()

        def calcular_troco(event=None):
            try:
                valor_recebido = float(valor_recebido_entry.get().replace(",", "."))
                troco = valor_recebido - total_pago
                label_troco.configure(text=f"Troco: R$ {troco:.2f}")
                if troco < 0:
                    label_troco.configure(text_color="red")
                else:
                    label_troco.configure(text_color="green")
            except ValueError:
                label_troco.configure(text="Troco: R$ 0.00", text_color="red")
        
        valor_recebido_entry.bind("<KeyRelease>", calcular_troco)
        
        def concluir_pagamento():
            if forma_pagamento_combo.get() == "":
                messagebox.showwarning("Atenção", "Por favor, selecione uma forma de pagamento.")
                return

            if forma_pagamento_combo.get() == "Dinheiro":
                if not valor_recebido_entry.get():
                    messagebox.showwarning("Atenção", "Por favor, digite o valor recebido.")
                    return
                try:
                    valor_recebido = float(valor_recebido_entry.get().replace(",", "."))
                    if valor_recebido < total_pago:
                        messagebox.showwarning("Atenção", "O valor recebido é menor que o total da compra.")
                        return
                except ValueError:
                    messagebox.showwarning("Atenção", "Valor recebido inválido.")
                    return
            
            if not messagebox.askyesno("Confirmação", "Deseja concluir o pagamento?"):
                return
            
            itens_da_venda = []
            itens_a_dar_baixa = []

            for item in carrinho_tabela.get_children():
                item_vals = carrinho_tabela.item(item)["values"]
                item_dict = {
                    "id_produto": item_vals[0],
                    "nome_produto": item_vals[1],
                    "quantidade": item_vals[2],
                    "preco_unitario": item_vals[3],
                    "subtotal": item_vals[4]
                }
                itens_da_venda.append(item_dict)
                if "temp_" not in str(item_vals[0]):
                    itens_a_dar_baixa.append({"id": item_vals[0], "quantidade": item_vals[2]})
            
            venda = {
                "id_cliente": cliente_selecionado["id"],
                "nome_cliente": cliente_selecionado["nome"],
                "itens": itens_da_venda,
                "total_bruto": total_bruto_var.get(),
                "desconto": desconto_var.get(),
                "total_final": total_final_var.get(),
                "forma_pagamento": forma_pagamento_combo.get(),
                "valor_recebido": valor_recebido_entry.get() or "N/A",
                "troco": label_troco.cget("text").replace("Troco: R$ ", "") or "0.00",
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            if itens_a_dar_baixa:
                estoque.dar_baixa(itens_a_dar_baixa)

            salvar_venda(venda)
            messagebox.showinfo("Sucesso", "Venda finalizada com sucesso!")
            
            for item in carrinho_tabela.get_children():
                carrinho_tabela.delete(item)
            desconto_entry.delete(0, "end")
            desconto_entry.insert(0, "0.00")
            atualizar_totais()
            popup.destroy()

            produtos_tabela.delete(*produtos_tabela.get_children())
            novos_produtos = estoque.carregar_estoque()
            for produto in novos_produtos:
                produtos_tabela.insert("", "end", values=(
                    produto["id"],
                    produto["nome"],
                    produto["quantidade"],
                    produto["preco"]
                ))
            
            cliente_selecionado["id"] = None
            cliente_selecionado["nome"] = "Cliente Não Identificado"
            cliente_label_var.set("Cliente: Não Identificado")
            entry_cpf_cliente.delete(0, "end")
        
        frame_concluir = ctk.CTkFrame(popup, fg_color="transparent")
        frame_concluir.pack(pady=10)
        btn_concluir = ctk.CTkButton(frame_concluir, text="Concluir", command=concluir_pagamento, fg_color="green")
        btn_concluir.pack()
        
        popup.bind("<Return>", lambda e: concluir_pagamento())
        
        def atalho_pagamento_popup(event):
            tecla = event.keysym 
            formas_pagamento = {
                "F2": "Dinheiro",
                "F3": "Cartão de Crédito",
                "F4": "Pix",
                "F5": "Cartão de Débito"
            }
            if tecla in formas_pagamento:
                forma_pagamento_combo.set(formas_pagamento[tecla])
                combobox_changed(formas_pagamento[tecla])
                if tecla != "F2":
                    btn_concluir.focus()

        popup.bind("<F2>", atalho_pagamento_popup)
        popup.bind("<F3>", atalho_pagamento_popup)
        popup.bind("<F4>", atalho_pagamento_popup)
        popup.bind("<F5>", atalho_pagamento_popup)
        
    def adicionar_produto_temporario():
        popup = ctk.CTkToplevel(janela)
        popup.title("Adicionar Produto Avulso")
        popup.resizable(False, False)
        centralizar(popup, 350, 300)
        
        label_msg = ctk.CTkLabel(popup, text="", text_color="red", font=("Arial",10))
        label_msg.pack(pady=5)

        ctk.CTkLabel(popup, text="Nome:").pack(pady=(5,0))
        entry_nome = ctk.CTkEntry(popup); entry_nome.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Quantidade:").pack(pady=(5,0))
        entry_quant = ctk.CTkEntry(popup); entry_quant.pack(pady=2, fill="x", padx=20)
        ctk.CTkLabel(popup, text="Preço:").pack(pady=(5,0))
        entry_preco = ctk.CTkEntry(popup); entry_preco.pack(pady=2, fill="x", padx=20)

        def salvar_temporario():
            erros=[]
            nome = entry_nome.get(); quant_str = entry_quant.get(); preco_str = entry_preco.get()
            if not nome: erros.append("Nome: obrigatório")
            try: 
                quant = int(quant_str)
            except ValueError:
                erros.append("Quantidade: deve ser um número inteiro")
            try: 
                preco = float(preco_str.replace(',', '.'))
            except ValueError:
                erros.append("Preço: deve ser um número")
            if erros:
                label_msg.configure(text="\n".join(erros))
                return
            
            produto_temp = {
                "id": f"temp_{datetime.now().timestamp()}", 
                "nome": nome,
                "preco": f"R$ {preco:.2f}"
            }
            adicionar_ao_carrinho(produto_temp, quant)
            popup.destroy()

        btn_salvar = ctk.CTkButton(popup, text="Adicionar", command=salvar_temporario); btn_salvar.pack(pady=10)
        entry_nome.bind("<Return>", lambda e: salvar_temporario())
        entry_quant.bind("<Return>", lambda e: salvar_temporario())
        entry_preco.bind("<Return>", lambda e: salvar_temporario())

    def voltar():
        janela.destroy()
        if callback:
            callback()

    def adicionar_por_id():
        try:
            produto_id = int(entry_id_busca.get())
        except ValueError:
            messagebox.showwarning("Atenção", "O ID deve ser um número inteiro.")
            entry_id_busca.delete(0, "end")
            return
        
        produto_encontrado = next((prod for prod in lista_produtos if int(prod["id"]) == produto_id), None)
        
        if produto_encontrado:
            try:
                quantidade_desejada = int(entry_quantidade.get() or 1)
            except ValueError:
                messagebox.showwarning("Atenção", "A quantidade deve ser um número inteiro.")
                return
            adicionar_ao_carrinho(produto_encontrado, quantidade_desejada)
            entry_id_busca.delete(0, "end")
        else:
            messagebox.showwarning("Atenção", "Produto com o ID informado não foi encontrado.")
            entry_id_busca.delete(0, "end")
    
    def buscar_cliente_por_cpf():
        nonlocal cliente_selecionado
        # Remove a formatação para a busca
        cpf_sem_formatacao = re.sub(r"\D", "", entry_cpf_cliente.get().strip())
        
        if not cpf_sem_formatacao or len(cpf_sem_formatacao) != 11:
            cliente_selecionado = {"id": None, "nome": "Cliente Não Identificado"}
            cliente_label_var.set("Cliente: Não Identificado")
            messagebox.showwarning("Atenção", "Por favor, digite um CPF válido (11 dígitos).")
            return

        lista_clientes = clientes.carregar_clientes()
        cliente_encontrado = next((c for c in lista_clientes if c.get("cpf") == cpf_sem_formatacao), None)

        if cliente_encontrado:
            cliente_selecionado["id"] = cliente_encontrado["id"]
            cliente_selecionado["nome"] = cliente_encontrado["nome"]
            cliente_label_var.set(f"Cliente: {cliente_encontrado['nome']}")
            messagebox.showinfo("Sucesso", f"Cliente {cliente_encontrado['nome']} encontrado e adicionado à venda.")
        else:
            cliente_selecionado["id"] = None
            cliente_selecionado["nome"] = "Cliente Não Identificado"
            cliente_label_var.set("Cliente: Não Identificado")
            messagebox.showwarning("Atenção", "Cliente não encontrado com o CPF informado.")
            
    janela.bind("<F11>", lambda e: finalizar_venda())

    frame_principal = ctk.CTkFrame(janela)
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
    
    frame_cliente = ctk.CTkFrame(frame_principal, fg_color="transparent")
    frame_cliente.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(frame_cliente, text="Buscar Cliente por CPF:", font=("Arial", 12)).pack(side="left", padx=(0, 5))
    entry_cpf_cliente = ctk.CTkEntry(frame_cliente, width=150, placeholder_text="CPF do Cliente")
    entry_cpf_cliente.pack(side="left", padx=(0, 5))
    
    entry_cpf_cliente.bind("<KeyRelease>", lambda e: formatar_e_validar_cpf(entry_cpf_cliente))
    entry_cpf_cliente.bind("<Return>", lambda e: buscar_cliente_por_cpf())
    
    btn_buscar_cliente = ctk.CTkButton(frame_cliente, text="Buscar", command=buscar_cliente_por_cpf)
    btn_buscar_cliente.pack(side="left", padx=(0, 10))
    
    label_cliente_identificado = ctk.CTkLabel(frame_cliente, textvariable=cliente_label_var, font=("Arial", 12, "bold"), text_color="cyan")
    label_cliente_identificado.pack(side="left", fill="x", expand=True)

    frame_conteudo = ctk.CTkFrame(frame_principal, fg_color="transparent")
    frame_conteudo.pack(fill="both", expand=True)
    
    frame_produtos = ctk.CTkFrame(frame_conteudo)
    frame_produtos.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=0)
    
    ctk.CTkLabel(frame_produtos, text="Produtos em Estoque", font=("Arial", 16, "bold")).pack(pady=(0, 10))
    
    frame_add = ctk.CTkFrame(frame_produtos, fg_color="transparent")
    frame_add.pack(fill="x", pady=(0, 5))

    ctk.CTkLabel(frame_add, text="Qtd:", font=("Arial", 12)).pack(side="left", padx=(0,5))
    entry_quantidade = ctk.CTkEntry(frame_add, width=50, placeholder_text="1")
    entry_quantidade.pack(side="left")

    ctk.CTkLabel(frame_add, text="ID:", font=("Arial", 12)).pack(side="left", padx=(15,5))
    entry_id_busca = ctk.CTkEntry(frame_add, width=80, placeholder_text="ID do Produto")
    entry_id_busca.pack(side="left")
    entry_id_busca.bind("<Return>", lambda e: adicionar_por_id())
    
    produtos_tabela = ttk.Treeview(frame_produtos, columns=("id", "nome", "quantidade", "preco"), show="headings")
    produtos_tabela.heading("id", text="ID"); produtos_tabela.heading("nome", text="Nome")
    produtos_tabela.heading("quantidade", text="Qtd"); produtos_tabela.heading("preco", text="Preço")
    
    produtos_tabela.column("id", width=40); produtos_tabela.column("nome", width=150)
    produtos_tabela.column("quantidade", width=50); produtos_tabela.column("preco", width=80)
    
    produtos_tabela.pack(fill="both", expand=True)

    for produto in lista_produtos:
        produtos_tabela.insert("", "end", values=(
            produto["id"],
            produto["nome"],
            produto["quantidade"],
            produto["preco"]
        ))
    
    produtos_tabela.bind("<Double-1>", lambda e: adicionar_selecionado())
    
    def adicionar_selecionado():
        selected = produtos_tabela.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um produto para adicionar ao carrinho.")
            return
        
        try:
            quantidade_desejada = int(entry_quantidade.get() or 1)
        except ValueError:
            messagebox.showwarning("Atenção", "A quantidade deve ser um número inteiro.")
            return

        item_id = selected[0]
        produto_id = produtos_tabela.item(item_id)["values"][0] 
        produto_selecionado = next((prod for prod in lista_produtos if int(prod["id"]) == produto_id), None)
        
        if produto_selecionado:
            adicionar_ao_carrinho(produto_selecionado, quantidade_desejada)

    frame_botoes_produtos = ctk.CTkFrame(frame_produtos, fg_color="transparent")
    frame_botoes_produtos.pack(pady=10)
    
    btn_add_carrinho = ctk.CTkButton(frame_botoes_produtos, text="Adicionar ao Carrinho", command=adicionar_selecionado)
    btn_add_carrinho.pack(side="left", padx=5)
    
    btn_add_avulso = ctk.CTkButton(frame_botoes_produtos, text="Produto Avulso", command=adicionar_produto_temporario)
    btn_add_avulso.pack(side="left", padx=5)
    
    frame_carrinho = ctk.CTkFrame(frame_conteudo)
    frame_carrinho.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=0)

    ctk.CTkLabel(frame_carrinho, text="Carrinho de Compras", font=("Arial", 16, "bold")).pack(pady=(0, 10))

    carrinho_tabela = ttk.Treeview(frame_carrinho, columns=("id", "nome", "quantidade", "preco_unitario", "subtotal"), show="headings")
    carrinho_tabela.heading("id", text="ID"); carrinho_tabela.heading("nome", text="Produto")
    carrinho_tabela.heading("quantidade", text="Qtd"); carrinho_tabela.heading("preco_unitario", text="Preço Unit.")
    carrinho_tabela.heading("subtotal", text="Subtotal")
    
    carrinho_tabela.column("id", width=30); carrinho_tabela.column("nome", width=120)
    carrinho_tabela.column("quantidade", width=50); carrinho_tabela.column("preco_unitario", width=80)
    carrinho_tabela.column("subtotal", width=90)
    
    carrinho_tabela.pack(fill="both", expand=True)
    
    frame_valores = ctk.CTkFrame(frame_carrinho, fg_color="transparent")
    frame_valores.pack(fill="x", pady=(10, 5))

    ctk.CTkLabel(frame_valores, text="Total Bruto:", font=("Arial", 14)).pack(side="left", padx=(0, 10))
    ctk.CTkLabel(frame_valores, textvariable=total_bruto_var, font=("Arial", 14, "bold")).pack(side="left")

    frame_desconto = ctk.CTkFrame(frame_valores, fg_color="transparent")
    frame_desconto.pack(side="right", padx=(10, 0))
    
    desconto_combo = ctk.CTkComboBox(frame_desconto, values=["Valor", "%"], width=80, command=lambda e: atualizar_totais(), state="readonly")
    desconto_combo.pack(side="left", padx=(0, 5))
    desconto_combo.set("Valor")

    desconto_entry = ctk.CTkEntry(frame_desconto, width=60, placeholder_text="0.00")
    desconto_entry.pack(side="left", padx=(0, 5))
    desconto_entry.bind("<Return>", lambda e: atualizar_totais())
    
    ctk.CTkLabel(frame_desconto, text="Desconto:", font=("Arial", 14)).pack(side="left", padx=(0, 10))

    frame_total_final = ctk.CTkFrame(frame_carrinho, fg_color="transparent")
    frame_total_final.pack(fill="x", pady=5)
    
    ctk.CTkLabel(frame_total_final, text="Total Final:", font=("Arial", 16, "bold")).pack(side="left", padx=(0, 10))
    ctk.CTkLabel(frame_total_final, textvariable=total_final_var, font=("Arial", 16, "bold"), text_color="green").pack(side="left")

    frame_botoes_principais = ctk.CTkFrame(janela, fg_color=None)
    frame_botoes_principais.pack(fill="x", pady=10, padx=20)
    
    ctk.CTkButton(frame_botoes_principais, text="Remover do Carrinho", command=remover_do_carrinho, width=150, fg_color="gray").pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes_principais, text="Finalizar Venda", command=finalizar_venda, width=150, fg_color="green").pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes_principais, text="Voltar", command=voltar, fg_color="red", width=150).pack(side="left", padx=5)

    janela.protocol("WM_DELETE_WINDOW", voltar)