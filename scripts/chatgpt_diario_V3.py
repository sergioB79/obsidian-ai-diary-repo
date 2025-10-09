import json
import os
import zipfile
from datetime import datetime
from collections import Counter
import re
import textwrap

# === CONFIGURAÇÃO ===
ZIP_PATH = r"________________insere aqui_______"
OUTPUT_DIR = r"________________insere aqui_______"

# === FUNÇÕES ===

def extract_zip(zip_path, extract_to):
    """Extrai o ficheiro .zip exportado do ChatGPT."""
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def clean_text(text):
    """Remove espaços desnecessários e caracteres estranhos."""
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()

def generate_tags(text, n=5):
    """Gera tags simples com base nas palavras mais frequentes."""
    words = re.findall(r"\b[a-zA-Záéíóúãõç]+\b", text.lower())
    stopwords = set(["o", "a", "os", "as", "de", "do", "da", "e", "em", "que",
                     "um", "uma", "para", "com", "no", "na"])
    words = [w for w in words if w not in stopwords and len(w) > 3]
    common = [w for w, _ in Counter(words).most_common(n)]
    return ", ".join(common)

def summarize_text(text, max_len=300):
    """Cria um pequeno resumo (1-2 linhas) com as primeiras frases."""
    text = clean_text(text)
    if len(text) > max_len:
        text = text[:max_len] + "..."
    return textwrap.fill(text, 120)

def safe_filename(name, max_len=60):
    """Garante nomes de ficheiro válidos e seguros para Windows."""
    if not isinstance(name, str):
        name = str(name)
    name = name.strip().replace("\n", " ").replace("\r", " ")
    name = re.sub(r'[\\/*?:"<>|~]', "", name)
    name = re.sub(r"\s+", " ", name)
    if len(name) > max_len:
        name = name[:max_len].rstrip() + "..."
    return name or "Sem_titulo"

def parse_date(create_time):
    """Lida com timestamps ou strings ISO."""
    if not create_time:
        return "Data desconhecida"
    try:
        return datetime.fromtimestamp(float(create_time)).strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        try:
            return datetime.fromisoformat(str(create_time).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(create_time)

def convert_to_markdown(json_folder, output_dir):
    """Cria ficheiros .md individuais e um INDEX.md com resumos."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index_path = os.path.join(output_dir, "INDEX.md")
    index_entries = []

    for root, _, files in os.walk(json_folder):
        for file in files:
            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao ler {file}: {e}")
                continue

            conversations = data if isinstance(data, list) else [data]

            for conv in conversations:
                title = conv.get("title", "Sem título")
                date = parse_date(conv.get("create_time"))
                mapping = conv.get("mapping", {})
                messages = []

                for msg in mapping.values():
                    if not isinstance(msg, dict):
                        continue
                    message = msg.get("message")
                    if not message:
                        continue

                    role = message.get("author", {}).get("role")
                    parts = message.get("content", {}).get("parts", [])

                    safe_parts = []
                    for p in parts:
                        if isinstance(p, str):
                            safe_parts.append(p)
                        elif isinstance(p, dict):
                            txt = p.get("text") or p.get("caption") or json.dumps(p)
                            safe_parts.append(str(txt))
                        else:
                            safe_parts.append(str(p))

                    text = clean_text(" ".join(safe_parts))
                    if not text:
                        continue
                    if role == "user":
                        messages.append(f"**Tu:** {text}")
                    elif role == "assistant":
                        messages.append(f"**GPT:** {text}")

                if not messages:
                    continue

                combined_text = " ".join(messages)
                tags = generate_tags(combined_text)
                resumo = summarize_text(combined_text)
                date_prefix = parse_date(conv.get("create_time")).split(" ")[0]
                safe_title = safe_filename(title)
                filename = f"{date_prefix} - {safe_title}.md"
                filepath = os.path.join(output_dir, filename)

                # Escreve o ficheiro individual
                try:
                    with open(filepath, "w", encoding="utf-8") as md:
                        md.write(f"# {title}\n")
                        md.write(f"🗓️ {date}\n\n")
                        md.write(f"**Tags:** {tags}\n\n")
                        md.write("\n".join(messages))
                        md.write("\n")
                except OSError as e:
                    print(f"⚠️ Erro ao criar {filename}: {e}")
                    continue

                index_entries.append({
                    "title": title,
                    "date": date,
                    "tags": tags,
                    "file": filename,
                    "summary": resumo
                })

    # Cria INDEX.md
    with open(index_path, "w", encoding="utf-8") as idx:
        idx.write("# 📚 Diário Automático ChatGPT — Índice\n\n")
        for e in sorted(index_entries, key=lambda x: x["date"], reverse=True):
            idx.write(f"## [{e['title']}]({e['file']})\n")
            idx.write(f"🗓️ {e['date']}\n\n")
            idx.write(f"**Tags:** {e['tags']}\n\n")
            idx.write(f"{e['summary']}\n\n---\n\n")

    print(f"✅ Conversas exportadas: {len(index_entries)} ficheiros .md")
    print(f"📘 Índice criado em: {index_path}")

# === EXECUÇÃO ===
temp_folder = os.path.join(OUTPUT_DIR, "temp_extract")
extract_zip(ZIP_PATH, temp_folder)
convert_to_markdown(temp_folder, OUTPUT_DIR)