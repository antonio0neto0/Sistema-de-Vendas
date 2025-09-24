import customtkinter as ctk
from PIL import Image
import sys

# Configurações globais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Funções de ações (por enquanto só prints)
def abrir_vendas():
    print("Abrindo módulo de vendas...")

def abrir_estoque():
    print("Abrindo controle de estoque...")

def abrir_clientes():
    print("Abrindo cadastro de clientes...")

def sair():
    sys.exit()  # encerra todo o programa

# Janela principal
menu = ctk.CTk()
menu.title("Sistema de Vendas - Menu Principal")
menu.geometry("600x400")  # largura e altura fixas

# ==== FRAME DE TÍTULO ====
frame_titulo = ctk.CTkFrame(menu)
frame_titulo.pack(fill="x", pady=(20, 10), padx=20)

label = ctk.CTkLabel(frame_titulo, text="Bem-vindo ao Sistema de Vendas!", font=("Arial", 18, "bold"))
label.pack(pady=10)

# ==== FRAME DE BOTÕES COM MARGEM INTERNA ====
frame_botoes = ctk.CTkFrame(menu, fg_color=None)  # transparente para ficar mais clean
frame_botoes.pack(pady=10, padx=40, fill="both")  # margem maior horizontalmente e verticalmente

# ==== CARREGAR ÍCONES ====
icone_vendas = ctk.CTkImage(light_image=Image.open("imagens/vendas.png"), size=(20, 20))
icone_estoque = ctk.CTkImage(light_image=Image.open("imagens/estoque.png"), size=(20, 20))
icone_clientes = ctk.CTkImage(light_image=Image.open("imagens/clientes.png"), size=(20, 20))
icone_sair = ctk.CTkImage(light_image=Image.open("imagens/sair.png"), size=(20, 20))

# ==== BOTÕES COM MESMO TAMANHO, CENTRALIZADOS E MARGEM INTERNA ====
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
                         command=sair, compound="left", width=botao_largura, height=botao_altura)
btn_sair.pack(pady=12, anchor="center")

menu.mainloop()
