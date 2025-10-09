import os, re, json
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util

# === CONFIGURAÇÃO ===
VAULT = r"________________insere aqui_______"   # <- a tua pasta com os .md
TOPICS_JSON = r"________________insere aqui_______"   # <- o teu .jason com as categorias
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 3                # máximo de temas atribuídos a cada nota
SIM_THRESHOLD = 0.28     # limiar mínimo de similaridade (0..1). Ajusta se quiseres.

# === UTIL ===

def read_topics(path: str) -> Dict[str, List[str]]:
    with open(path, encoding="utf-8") as f:
        topics = json.load(f)
    # normaliza chaves para slugs simples (sem espaços/acentos) mas mantém label original
    clean = {}
    for k, seeds in topics.items():
        slug = re.sub(r"[^a-z0-9_-]+", "", k.lower())
        clean[slug or k.lower()] = {"label": k, "seeds": seeds}
    return clean

def first_n_chars(text: str, n: int = 1500) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    return t[:n]

def is_tags_line(line: str) -> bool:
    # linha composta por 2+ hashtags (ex.: #filosofia #tria)
    return bool(re.fullmatch(r"(?:#[\w\-]+\s*){2,}", line.strip(), flags=re.UNICODE))

# === MAIN ===

def main():
    model = SentenceTransformer(MODEL_NAME)
    topics = read_topics(TOPICS_JSON)

    # pré-calcula embedding de cada tema (média das seeds)
    topic_vecs = {}
    for slug, entry in topics.items():
        seeds_text = " | ".join(entry["seeds"])
        topic_vecs[slug] = model.encode(seeds_text, normalize_embeddings=True)

    vault = Path(VAULT)
    md_files = list(vault.rglob("*.md"))
    changed = 0
    counts = {slug: 0 for slug in topics}

    for path in md_files:
        # lê
        text = path.read_text(encoding="utf-8", errors="ignore")

        # extrai conteúdo (ignora frontmatter; usamos tudo porque não tens YAML)
        summary = first_n_chars(text, 1500)

        # embedding da nota
        note_vec = model.encode(summary, normalize_embeddings=True)

        # mede similaridades
        sims = {
            slug: float(util.cos_sim(note_vec, vec))
            for slug, vec in topic_vecs.items()
        }
        # ordena por similaridade
        ordered = sorted(sims.items(), key=lambda x: x[1], reverse=True)

        # escolhe top temas acima do limiar
        chosen = [slug for slug, s in ordered if s >= SIM_THRESHOLD][:TOP_K]
        if not chosen:
            # se nada passou o limiar, ainda escolhemos o melhor 1 para não ficar sem tag
            chosen = [ordered[0][0]] if ordered else []

        # cria linha de tags semânticas
        tag_line = " ".join(f"#{topics[slug]['label'].lower().replace(' ', '')}" for slug in chosen).strip()
        if not tag_line:
            continue

        # atualiza contadores
        for c in chosen:
            counts[c] += 1

        # insere/substitui no topo (depois da linha da data, se existir)
        lines = text.splitlines()
        insert_idx = 0

        # tenta encontrar a linha da data (ex.: começa com emoji calendário ou YYYY-MM-DD)
        for i, ln in enumerate(lines[:10]):
            if ln.strip().startswith("🗓") or re.search(r"\d{4}-\d{2}-\d{2}", ln):
                insert_idx = i + 1
                break

        # se a linha seguinte já for uma linha de hashtags, substitui; senão, insere
        # também apanha a linha de tags antiga do v3 (hashtags logo após a data)
        j = insert_idx
        # salta linhas vazias
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and is_tags_line(lines[j]):
            lines[j] = tag_line
        else:
            lines.insert(insert_idx, tag_line)
            # mantém uma linha vazia depois para separar
            lines.insert(insert_idx + 1, "")

        new_text = "\n".join(lines)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1

    # cria índice de temas
    idx_path = vault / "TagIndex.md"
    with open(idx_path, "w", encoding="utf-8") as out:
        out.write("# 🗂️ Índice de Temas (Semânticos)\n\n")
        for slug, n in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            label = topics[slug]["label"]
            out.write(f"- **#{label.lower().replace(' ', '')}** — {n} notas\n")

    print(f"✅ Notas processadas: {len(md_files)} | Atualizadas: {changed}")
    print(f"📘 Índice criado em: {idx_path}")

if __name__ == "__main__":
    main()
