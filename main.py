import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

DATA_FILE = 'pokemon_collection.json'

# Funções para manipular os dados locais
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Função para buscar Pokémon na PokeAPI
def fetch_pokemon(identifier):
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        types = [t['type']['name'] for t in data['types']]
        return {
            "id": data['id'],
            "name": data['name'].capitalize(),
            "types": types,
            "quantidade": 0
        }
    except requests.RequestException:
        messagebox.showerror("Erro", "Pokémon não encontrado! Verifique o ID ou nome digitado.")
        return None

# Adicionar Pokémon
def add_pokemon():
    identifier = entry_pokemon_id.get().strip()
    if not identifier:
        messagebox.showerror("Erro", "Por favor, insira um ID ou nome válido.")
        return

    if identifier.isdigit():
        identifier = int(identifier)  # Converte para número se for ID

    if str(identifier).lower() in data or str(identifier) in data:
        messagebox.showinfo("Aviso", f"O Pokémon já está na coleção.")
        return

    pokemon = fetch_pokemon(identifier)
    if pokemon:
        data[str(pokemon['id'])] = pokemon
        save_data(data)
        update_table()
        messagebox.showinfo("Sucesso", f"{pokemon['name']} adicionado à coleção!")

# Atualizar quantidade de Pokémon
def update_quantity():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Por favor, selecione um Pokémon na tabela.")
        return

    pokemon_id = table.item(selected_item, "values")[0]
    try:
        quantity_change = int(entry_quantity.get().strip())
        new_quantity = max(0, data[pokemon_id]['quantidade'] + quantity_change)
        data[pokemon_id]['quantidade'] = new_quantity
        save_data(data)
        update_table()
        messagebox.showinfo("Sucesso", f"A quantidade de {data[pokemon_id]['name']} foi atualizada para {new_quantity}.")
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido para a quantidade.")

# Atualizar tabela
def update_table():
    for row in table.get_children():
        table.delete(row)

    for pokemon_id, details in data.items():
        table.insert("", "end", values=(pokemon_id, details['name'], ', '.join(details['types']), details['quantidade']))

# Criar janela principal
data = load_data()
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
table.pack(fill="both", expand=True)

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center")

update_table()

# Rodar a aplicação
root.mainloop()
