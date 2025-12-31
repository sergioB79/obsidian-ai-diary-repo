
# Obsidian AI Diary — from ChatGPT to a Live, Shareable Vault

Turn **ChatGPT exports** into an **interactive Obsidian vault** with semantic tags and links.

<img width="2048" height="1591" alt="image" src="https://github.com/user-attachments/assets/13bc6415-b636-454f-83b6-4c727665d64c" />


> Portuguese guide included in `docs/Guia-PT.md`. This repo is designed to be **beginner-friendly** with or without prior Git knowledge.

## Features
- 🧰 Scripts to convert ChatGPT export `.zip` → Markdown notes (`.md`) + `INDEX.md`  
- 🏷️ **Semantic tags** (multilingual) using sentence-transformers  
- 🔗 **Related-note linking** blocks (Obsidian wikilinks)  
- 🧼 Cleaner for heavy JSON/media blocks that freeze Obsidian  
- 🗂️ Ready-to-publish structure for **GitHub** (share, backup, version)  

## Quickstart
1. **Install** Python 3.10+ and run:
   ```bash
   pip install -U -r requirements.txt
   ```
2. **Export** your ChatGPT data: *ChatGPT → Settings → Data Controls → Export Data* (`.zip`).  
3. **Convert to Obsidian notes**:
   ```bash
   python scripts/chatgpt_diario_v3.py
   ```
   Edit paths inside the script or via env vars.
4. **Open folder as vault** in Obsidian.  
5. **Add semantic tags**:
   ```bash
   python scripts/semantic_tag_vault.py
   ```
6. **Add related links**:
   ```bash
   python scripts/semantic_link_vault.py
   ```
7. (Optional) **Clean heavy notes** if Obsidian freezes:
   ```bash
   python scripts/clean_sediment_md.py
   ```

## Folders
```
/scripts   # python scripts + topics.json
/docs      # guides (EN/PT)
/examples  # sample config / paths
```

## License
MIT — feel free to adapt.
