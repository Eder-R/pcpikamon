''' Pokedex em python '''
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import requests
from PIL import Image, ImageTk

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pokemon_collection.json')

# Funções para manipular os dados locais
def load_data():
    """
    Carrega os dados da coleção de Pokémon a partir de um arquivo JSON.

    Se o arquivo não existir, retorna um dicionário vazio.

    Returns:
        dict: Dados da coleção de Pokémon.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def save_data(data):
    """
    Salva os dados da coleção de Pokémon em um arquivo JSON.

    Args:
        data (dict): Dados da coleção de Pokémon a serem salvos.
    """
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# Função para buscar Pokémon na PokeAPI
def fetch_pokemon(identifier):
    """
    Busca informações de um Pokémon na PokeAPI com base no identificador fornecido.

    Args:
        identifier (str | int): ID ou nome do Pokémon.

    Returns:
        dict | None: Dados do Pokémon ou None se houver um erro na requisição.
    """
    try:
        if isinstance(identifier, int) or identifier.isdigit():
            url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
        else:
            identifier = identifier.lower()
            url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        types = [t['type']['name'] for t in data['types']]
        sprite_url = data['sprites']['front_default']

        return {
            "id": data['id'],
            "name": data['name'].capitalize(),
            "types": types,
            "sprite": sprite_url,
            "quantidade": 0
        }
    except requests.RequestException:
        messagebox.showerror("Erro", "Pokémon não encontrado! Verifique o ID ou nome digitado.")
        return None

# Adicionar Pokémon
def add_pokemon():
    """
    Adiciona um Pokémon à coleção com base no ID ou nome fornecido pelo usuário.

    Verifica se o Pokémon já está na coleção antes de adicionar.
    Se o Pokémon for adicionado com sucesso, a tabela é atualizada,
    e uma mensagem de sucesso é exibida.
    """
    identifier = entry_pokemon_id.get().strip()
    if not identifier:
        messagebox.showerror("Erro", "Por favor, insira um ID ou nome válido.")
        return

    if identifier.isdigit():
        identifier = int(identifier)

    if str(identifier).lower() in pokemon_data or str(identifier) in pokemon_data:
        messagebox.showinfo("Aviso", "O Pokémon já está na coleção.")
        return

    pokemon = fetch_pokemon(identifier)
    if pokemon:
        pokemon_data[str(pokemon['id'])] = pokemon
        save_data(pokemon_data)
        update_table()
        messagebox.showinfo("Sucesso", f"{pokemon['name']} adicionado à coleção!")

# Atualizar quantidade de Pokémon
def update_quantity():
    """
    Atualiza a quantidade de um Pokémon na coleção com base,
    na seleção da tabela e valor inserido pelo usuário.

    A quantidade é ajustada para um valor não negativo.
    Se a operação for bem-sucedida, a tabela é atualizada e,
    uma mensagem de sucesso é exibida.
    """
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Por favor, selecione um Pokémon na tabela.")
        return

    pokemon_id = table.item(selected_item, "values")[0]
    try:
        quantity_change = int(entry_quantity.get().strip())
        new_quantity = max(0, pokemon_data[pokemon_id]['quantidade'] + quantity_change)
        pokemon_data[pokemon_id]['quantidade'] = new_quantity
        save_data(pokemon_data)
        update_table()
        messagebox.showinfo("Sucesso",
                            f"A quantidade de {pokemon_data[pokemon_id]['name']}" 
                            "foi atualizada para {new_quantity}.")
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido para a quantidade.")

# Atualizar tabela com ordenação
def update_table():
    """
    Atualiza a tabela de Pokémon na interface gráfica.

    Ordena os Pokémon por ID e preenche a tabela com as informações da coleção.
    """
    # Limpa a tabela
    for row in table.get_children():
        table.delete(row)

    # Ordena os Pokémon pelo ID
    sorted_data = sorted(pokemon_data.items(), key=lambda item: int(item[0]))

    # Preenche a tabela com os dados ordenados
    for pokemon_id, details in sorted_data:
        table.insert("", "end", values=(
            pokemon_id,
            details['name'],
            ', '.join(details['types']),
            details['quantidade']
        ))

# Exibir sprite do Pokémon selecionado
def show_sprite(event):
    """
    Exibe o sprite do Pokémon selecionado na tabela.

    Baixa a imagem do sprite a partir da URL e redimensiona a imagem para exibição.
    Se houver algum erro ao carregar a imagem, uma mensagem de erro será exibida.
    """
    selected_item = table.selection()
    if not selected_item:
        sprite_label.configure(image=None)
        sprite_label.image = None
        return

    pokemon_id = table.item(selected_item, "values")[0]
    sprite_url = pokemon_data[pokemon_id]['sprite']

    # Baixar e redimensionar a imagem
    try:
        response = requests.get(sprite_url, stream=True, timeout=5)
        response.raise_for_status()

        image_data = response.raw
        image = Image.open(image_data)
        image = image.resize((100, 100), Image.Resampling.LANCZOS)

        sprite_image = ImageTk.PhotoImage(image)

        # Atualizar o Label do sprite
        sprite_label.configure(image=sprite_image)
        sprite_label.image = sprite_image  # Salvar referência para evitar garbage collection

    except requests.RequestException:
        messagebox.showerror("Erro", "Falha ao carregar o sprite do Pokémon.")

# Criar janela principal
pokemon_data = load_data()
root = tk.Tk()
root.title("Pokédex Pokémon GO")

# Frame para adicionar Pokémon
frame_add = ttk.LabelFrame(root, text="Adicionar Pokémon")
frame_add.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_add, text="ID ou Nome do Pokémon:").grid(row=0, column=0, padx=5, pady=5)
entry_pokemon_id = ttk.Entry(frame_add)
entry_pokemon_id.grid(row=0, column=1, padx=5, pady=5)

btn_add_pokemon = ttk.Button(frame_add, text="Adicionar", command=add_pokemon)
btn_add_pokemon.grid(row=0, column=2, padx=5, pady=5)

# Frame para atualizar quantidade
frame_update = ttk.LabelFrame(root, text="Atualizar Quantidade")
frame_update.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_update, text="Alterar Quantidade:").grid(row=0, column=0, padx=5, pady=5)
entry_quantity = ttk.Entry(frame_update)
entry_quantity.grid(row=0, column=1, padx=5, pady=5)

btn_update_quantity = ttk.Button(frame_update, text="Atualizar", command=update_quantity)
btn_update_quantity.grid(row=0, column=2, padx=5, pady=5)

# Tabela de Pokémon
frame_table = ttk.LabelFrame(root, text="Coleção de Pokémon")
frame_table.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("ID", "Nome", "Tipos", "Quantidade")
table = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)
table.pack(side="left", fill="both", expand=True)

# Ajustar as colunas
table.column("ID", width=50, anchor="center")
table.column("Nome", width=150, anchor="center")
table.column("Tipos", width=200, anchor="center")
table.column("Quantidade", width=100, anchor="center")

# Configurar os cabeçalhos
for col in columns:
    table.heading(col, text=col)

# Exibição de sprite
sprite_label = ttk.Label(frame_table)
sprite_label.pack(side="right", padx=10, pady=10)

# Eventos
table.bind("<<TreeviewSelect>>", show_sprite)

update_table()

# Rodar a aplicação
root.mainloop()
