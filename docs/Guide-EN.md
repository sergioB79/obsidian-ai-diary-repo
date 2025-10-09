
# Obsidian AI Diary — Guide (EN)

This repository turns ChatGPT exports into an Obsidian vault with semantic tags and links.

## Pipeline
1. Export ChatGPT data (.zip)
2. `chatgpt_diario_v3.py` → Markdown files + INDEX.md
3. `semantic_tag_vault.py` → semantic tags from `topics.json`
4. `semantic_link_vault.py` → related-notes block
5. `clean_sediment_md.py` → remove heavy JSON/media blocks

## Tips
- Use `sentence-transformers` (paraphrase-multilingual-MiniLM-L12-v2) for multilingual tagging.
- If Obsidian indexing is slow: remove `temp_extract`, split by year, temporarily disable heavy plugins.
- Share on GitHub with **GitHub Desktop** or the **Obsidian Git** plugin.
