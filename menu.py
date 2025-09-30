import customtkinter as ctk
from PIL import Image
import sys
import vendas
import estoque
from login import abrir_login

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def iniciar_sistema():
    # === Menu principal ===
    menu = ctk.CTk()
    menu.title("Sistema de Vendas - Menu Principal")
    menu.geometry("600x400")

    # Menu escondido até login
    menu.withdraw()

    # === Callback após login ===
    def mostrar_menu():
        menu.deiconify()

    # Abre o login modal
    abrir_login(menu, callback_login_sucesso=mostrar_menu)

    # === Frame Título ===
    frame_titulo = ctk.CTkFrame(menu)
    frame_titulo.pack(fill="x", pady=(20,10), padx=20)
    label = ctk.CTkLabel(frame_titulo, text="Bem-vindo ao Sistema de Vendas!", font=("Arial",18,"bold"))
    label.pack(pady=10)

    # === Frame Botões ===
    frame_botoes = ctk.CTkFrame(menu, fg_color=None)
    frame_botoes.pack(pady=10, padx=40, fill="both")

    # === Ícones ===
    try:
        icone_vendas = ctk.CTkImage(light_image=Image.open("imagens/vendas.png"), size=(20,20))
        icone_estoque = ctk.CTkImage(light_image=Image.open("imagens/estoque.png"), size=(20,20))
        icone_clientes = ctk.CTkImage(light_image=Image.open("imagens/clientes.png"), size=(20,20))
        icone_sair = ctk.CTkImage(light_image=Image.open("imagens/sair.png"), size=(20,20))
    except:
        icone_vendas = icone_estoque = icone_clientes = icone_sair = None

    largura = 180
    altura = 35

    # === Funções dos Botões ===
    def abrir_vendas():
        menu.iconify()
        vendas.abrir_vendas(menu, callback=lambda: menu.deiconify())

    def abrir_estoque_callback():
        menu.iconify()
        estoque.abrir_estoque(menu, callback=lambda: menu.deiconify())

    import clientes

    def abrir_clientes():
        menu.iconify()
        clientes.abrir_clientes(menu, callback=lambda: menu.deiconify())


    def sair():
        menu.destroy()
        sys.exit()

    # === Botões ===
    btn_vendas = ctk.CTkButton(frame_botoes, text="Nova Venda", image=icone_vendas,
                               command=abrir_vendas, compound="left",
                               width=largura, height=altura)
    btn_vendas.pack(pady=8, anchor="center")

    btn_estoque = ctk.CTkButton(frame_botoes, text="Controle de Estoque", image=icone_estoque,
                                command=abrir_estoque_callback, compound="left",
                                width=largura, height=altura)
    btn_estoque.pack(pady=8, anchor="center")

    btn_clientes = ctk.CTkButton(frame_botoes, text="Cadastro de Clientes", image=icone_clientes,
                                 command=abrir_clientes, compound="left",
                                 width=largura, height=altura)
    btn_clientes.pack(pady=8, anchor="center")

    btn_sair = ctk.CTkButton(frame_botoes, text="Sair", image=icone_sair,
                             fg_color="red", command=sair, compound="left",
                             width=largura, height=altura)
    btn_sair.pack(pady=12, anchor="center")

    # === Mainloop apenas no menu ===
    menu.mainloop()
