import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import json, os, csv
from datetime import datetime, timedelta
from fpdf import FPDF

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ARQUIVO_VENDAS = "vendas.json"

def centralizar(jan, largura, altura):
    x = (jan.winfo_screenwidth() // 2) - (largura // 2)
    y = (jan.winfo_screenheight() // 2) - (altura // 2)
    jan.geometry(f"{largura}x{altura}+{x}+{y}")

def carregar_historico_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        try:
            with open(ARQUIVO_VENDAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def abrir_historico_vendas(menu, callback=None):
    janela = ctk.CTkToplevel(menu)
    janela.title("Sistema de Vendas - Histórico de Vendas")
    janela.state("zoomed")  # maximizada

    # === Funções internas ===
    def voltar():
        janela.destroy()
        menu.deiconify()
        if callback:
            callback()

    dados = carregar_historico_vendas()

    # Filtro por período
    def atualizar_tabela(*args):
        periodo = periodo_var.get()
        cliente = cliente_entry.get().lower()

        tabela.delete(*tabela.get_children())
        total_geral = 0

        for venda in dados:
            # Apenas data dd/mm/aaaa
            data_venda_str = venda.get("data", "01/01/1900")
            try:
                data_venda = datetime.strptime(data_venda_str.split()[0], "%d/%m/%Y")
            except:
                continue

            incluir = False
            hoje = datetime.now()
            if periodo == "Todos":
                incluir = True
            elif periodo == "Últimos 7 dias":
                incluir = data_venda >= (hoje - timedelta(days=7))
            elif periodo == "Este mês":
                incluir = data_venda.month == hoje.month and data_venda.year == hoje.year
            elif periodo == "Personalizado":
                try:
                    inicio = datetime.strptime(entry_inicio.get(), "%d/%m/%Y")
                    fim = datetime.strptime(entry_fim.get(), "%d/%m/%Y")
                    incluir = inicio <= data_venda <= fim
                except:
                    incluir = False

            # Filtrar por cliente
            if cliente and cliente not in venda.get("nome_cliente","").lower():
                incluir = False

            if incluir:
                total = venda.get("total_final",0.0)
                total_geral += float(total)
                total_formatado = f"R$ {float(total):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                tabela.insert("", "end", values=(
                    data_venda.strftime("%d/%m/%Y"),
                    venda.get("id_cliente","N/A"),
                    venda.get("nome_cliente","Não Identificado"),
                    total_formatado,
                    venda.get("forma_pagamento","N/A")
                ))
        total_label.configure(text=f"Total Geral: R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # === Frame Título ===
    frame_titulo = ctk.CTkFrame(janela)
    frame_titulo.pack(fill="x", pady=(20, 10), padx=20)
    ctk.CTkLabel(frame_titulo, text="Histórico de Vendas", font=("Arial", 18, "bold")).pack(pady=10)

    # === Filtros ===
    frame_filtros = ctk.CTkFrame(janela, fg_color=None)
    frame_filtros.pack(fill="x", padx=20, pady=5)

    periodo_var = ctk.StringVar(value="Todos")
    ctk.CTkOptionMenu(frame_filtros, values=["Todos","Últimos 7 dias","Este mês","Personalizado"],
                       variable=periodo_var, command=lambda e=None: atualizar_campos_periodo()).pack(side="left", padx=5)

    cliente_entry = ctk.CTkEntry(frame_filtros, placeholder_text="Pesquisar por cliente")
    cliente_entry.pack(side="left", padx=5)
    cliente_entry.bind("<KeyRelease>", atualizar_tabela)

    # Campos personalizados
    entry_inicio = ctk.CTkEntry(frame_filtros, placeholder_text="dd/mm/aaaa", width=100)
    entry_fim = ctk.CTkEntry(frame_filtros, placeholder_text="dd/mm/aaaa", width=100)
    entry_inicio.pack(side="left", padx=5)
    entry_fim.pack(side="left", padx=5)

    entry_inicio.bind("<Return>", atualizar_tabela)
    entry_fim.bind("<Return>", atualizar_tabela)

    def atualizar_campos_periodo():
        if periodo_var.get() == "Personalizado":
            entry_inicio.configure(state="normal")
            entry_fim.configure(state="normal")
        else:
            entry_inicio.configure(state="disabled")
            entry_fim.configure(state="disabled")
        atualizar_tabela()

    # === Tabela de Vendas ===
    frame_tabela = ctk.CTkFrame(janela, fg_color=None)
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=10)

    colunas = ("data", "id_cliente", "nome_cliente", "total_final", "forma_pagamento")
    tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

    for c in colunas:
        tabela.heading(c, text=c.capitalize())
    tabela.column("data", width=100, anchor="center")
    tabela.column("id_cliente", width=80, anchor="center")
    tabela.column("nome_cliente", width=200, anchor="w")
    tabela.column("total_final", width=120, anchor="center")
    tabela.column("forma_pagamento", width=150, anchor="center")

    scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # === Rodapé com total ===
    frame_rodape = ctk.CTkFrame(janela, fg_color=None)
    frame_rodape.pack(fill="x", padx=20, pady=5)
    total_label = ctk.CTkLabel(frame_rodape, text="Total Geral: R$ 0,00", font=("Arial",12,"bold"))
    total_label.pack(side="right")

    # === Funções de exportação ===
    def exportar_csv():
        caminho = filedialog.asksaveasfilename(defaultextension=".csv",
                                               filetypes=[("CSV files","*.csv")])
        if not caminho:
            return
        with open(caminho, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=";")
            escritor.writerow(["Data","ID Cliente","Nome Cliente","Total Final","Forma de Pagamento"])
            for item in tabela.get_children():
                valores = tabela.item(item)["values"]
                escritor.writerow(valores)
        messagebox.showinfo("Exportação CSV", f"Histórico exportado para:\n{caminho}")

    def exportar_pdf():
        caminho = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF","*.pdf")])
        if not caminho:
            return
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial","B",14)
        pdf.cell(0,10,"Histórico de Vendas",0,1,"C")
        pdf.set_font("Arial","",12)
        pdf.ln(5)

        larguras = [30,20,60,30,40]
        cabecalho = ["Data","ID","Cliente","Total","Pagamento"]
        for i,text in enumerate(cabecalho):
            pdf.cell(larguras[i],10,text,1,0,"C")
        pdf.ln()
        for item in tabela.get_children():
            valores = tabela.item(item)["values"]
            for i,v in enumerate(valores):
                pdf.cell(larguras[i],10,str(v),1,0,"C")
            pdf.ln()
        pdf.ln(5)
        pdf.set_font("Arial","B",12)
        pdf.cell(0,10,total_label.cget("text"),0,1,"R")
        pdf.output(caminho)
        messagebox.showinfo("Exportação PDF", f"Histórico exportado para:\n{caminho}")

    # === Botões ===
    frame_botoes = ctk.CTkFrame(janela, fg_color=None)
    frame_botoes.pack(pady=10)
    ctk.CTkButton(frame_botoes, text="Exportar CSV", command=exportar_csv, width=150).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Exportar PDF", command=exportar_pdf, width=150).pack(side="left", padx=5)
    ctk.CTkButton(frame_botoes, text="Voltar", command=voltar, fg_color="red", width=150).pack(side="left", padx=5)

    # Inicializa
    atualizar_campos_periodo()
