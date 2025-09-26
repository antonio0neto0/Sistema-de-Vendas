import customtkinter as ctk
from PIL import Image
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def abrir_menu(janela_login):
    # Oculta a janela de login
    janela_login.withdraw()

    menu = ctk.CTkToplevel(janela_login)
    menu.title("Sistema de Vendas - Menu Principal")
    menu.geometry("600x400")

    # ===== Funções dos botões =====
    def abrir_vendas():
        print("Abrindo módulo de vendas...")

    def abrir_estoque():
        print("Abrindo controle de estoque...")

    def abrir_clientes():
        print("Abrindo cadastro de clientes...")

    def sair_menu():
        menu.destroy()
        janela_login.destroy()
        sys.exit()

    # ===== FRAME TÍTULO =====
    frame_titulo = ctk.CTkFrame(menu)
    frame_titulo.pack(fill="x", pady=(20,10), padx=20)
    label = ctk.CTkLabel(frame_titulo, text="Bem-vindo ao Sistema de Vendas!", font=("Arial", 18, "bold"))
    label.pack(pady=10)

    # ===== FRAME BOTÕES =====
    frame_botoes = ctk.CTkFrame(menu, fg_color=None)
    frame_botoes.pack(pady=10, padx=40, fill="both")

    # ===== CARREGAR ÍCONES =====
    try:
        icone_vendas = ctk.CTkImage(light_image=Image.open("imagens/vendas.png"), size=(20, 20))
        icone_estoque = ctk.CTkImage(light_image=Image.open("imagens/estoque.png"), size=(20, 20))
        icone_clientes = ctk.CTkImage(light_image=Image.open("imagens/clientes.png"), size=(20, 20))
        icone_sair = ctk.CTkImage(light_image=Image.open("imagens/sair.png"), size=(20, 20))
    except Exception as e:
        print("Erro ao carregar ícones:", e)
        icone_vendas = icone_estoque = icone_clientes = icone_sair = None

    botao_largura = 180
    botao_altura = 35

    btn_vendas = ctk.CTkButton(frame_botoes, text="Nova Venda", image=icone_vendas,
                               command=abrir_vendas, compound="left", width=botao_largura, height=botao_altura)
    btn_vendas.pack(pady=8, anchor="center")

    btn_estoque = ctk.CTkButton(frame_botoes, text="Controle de Estoque", image=icone_estoque,
                                command=abrir_estoque, compound="left", width=botao_largura, height=botao_altura)
    btn_estoque.pack(pady=8, anchor="center")

    btn_clientes = ctk.CTkButton(frame_botoes, text="Cadastro de Clientes", image=icone_clientes,
                                 command=abrir_clientes, compound="left", width=botao_largura, height=botao_altura)
    btn_clientes.pack(pady=8, anchor="center")

    btn_sair = ctk.CTkButton(frame_botoes, text="Sair", image=icone_sair, fg_color="red",
                             command=sair_menu, compound="left", width=botao_largura, height=botao_altura)
    btn_sair.pack(pady=12, anchor="center")
