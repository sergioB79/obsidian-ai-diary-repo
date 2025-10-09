import os
import re
import shutil

VAULT_DIR = r"________________insere aqui_______"

# padrões a remover: blocos JSON, pointers, e caracteres invisíveis
PATTERNS = [
    r"\{[^{}]*?(\"asset_pointer\"|\"file-service:\/\/\"|\"content_type\"|\"sediment:\/\/\"|\"search\d+\"|\"cite\").*?\}",  # blocos JSON
    r"||||turn\d+news\d+",  # caracteres estranhos de citações
    r"\"{2,}",  # aspas repetidas
    r"\\n",  # newlines literais
]

def clean_text(content: str) -> str:
    """Aplica regex e limpa texto."""
    for pattern in PATTERNS:
        content = re.sub(pattern, "", content, flags=re.DOTALL)
    # normaliza quebras de linha e espaços
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r" {2,}", " ", content)
    content = content.strip()
    return content

def clean_file(filepath: str) -> bool:
    """Remove blocos JSON e símbolos estranhos de um ficheiro Markdown."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not any(keyword in content for keyword in ["asset_pointer", "file-service://", "", "cite"]):
            return False  # nada a limpar

        cleaned = clean_text(content)

        # cria backup antes de reescrever
        backup_path = filepath + ".bak"
        if not os.path.exists(backup_path):
            shutil.copy(filepath, backup_path)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cleaned + "\n")

        return True

    except Exception as e:
        print(f"⚠️ Erro ao processar {filepath}: {e}")
        return False


def clean_vault(vault_dir: str):
    total, cleaned_count = 0, 0
    for root, _, files in os.walk(vault_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            total += 1
            path = os.path.join(root, f)
            if clean_file(path):
                cleaned_count += 1
                print(f"🧼 Limpo: {f}")
    print(f"\n✅ Processados: {total} | Ficheiros limpos: {cleaned_count}")
    print("💾 Backups (.bak) criados para todos os ficheiros alterados.")


if __name__ == "__main__":
    print("🔍 A limpar JSONs e metadados de multimédia...")
    clean_vault(VAULT_DIR)
