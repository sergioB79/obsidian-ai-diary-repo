import os
import re
from collections import defaultdict

VAULT_DIR = r"________________insere aqui_______"
MAX_LINKS = 8  # máximo de links por nota

def extract_tags(content):
    """Extrai tags (#algo) de uma nota"""
    return re.findall(r"#(\w+)", content)

def build_tag_index(vault_dir):
    """Mapeia tags -> lista de ficheiros"""
    tag_map = defaultdict(list)
    for root, _, files in os.walk(vault_dir):
        for f in files:
            if f.endswith(".md"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    tags = extract_tags(file.read())
                    for tag in set(tags):
                        tag_map[tag].append(path)
    return tag_map

def add_related_links(vault_dir, tag_map):
    for root, _, files in os.walk(vault_dir):
        for f in files:
            if not f.endswith(".md"):
                continue

            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            tags = extract_tags(content)
            if not tags:
                continue

            related_files = set()
            for tag in tags:
                for linked_file in tag_map.get(tag, []):
                    if linked_file != path:
                        related_files.add(linked_file)

            related_files = list(related_files)[:MAX_LINKS]
            if not related_files:
                continue

            # Gera o bloco de links
            links_section = "\n---\n**Ligações relacionadas**\n"
            for rel_path in related_files:
                title = os.path.splitext(os.path.basename(rel_path))[0]
                links_section += f"[[{title}]]\n"

            # Remove versões antigas do bloco, se existirem
            content = re.sub(r"\n---\n\*\*Ligações relacionadas\*\*[\s\S]*", "", content)

            # Adiciona o bloco novo no fim
            content += "\n" + links_section.strip() + "\n"

            with open(path, "w", encoding="utf-8", errors="ignore") as file:
                file.write(content)

if __name__ == "__main__":
    print("🔍 A mapear tags...")
    tag_map = build_tag_index(VAULT_DIR)
    print(f"✅ {len(tag_map)} tags detetadas. A criar ligações...")
    add_related_links(VAULT_DIR, tag_map)
    print("🕸️ Ligações semânticas adicionadas com sucesso!")
