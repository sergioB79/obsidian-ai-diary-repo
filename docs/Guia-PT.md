
# Do ChatGPT ao Obsidian — Diário Interativo (Guia PT)

Transformei **+20.000 conversas com IA** num **diário vivo** e o resultado é lindo... e **interativo**.  
Este guia mostra, passo a passo, como criar um diário de ideias, temas e **ligações semânticas** a partir das tuas conversas com IA.

---

## 0) Preparação

**Pasta de trabalho** (ex.): `C:\cgp-diary-agent\`  
**Python + deps:**
```bash
pip install -U sentence-transformers
```
(Obsidian instalado).

> Dica: também podes `pip install -r requirements.txt` na raiz do projeto.

---

## 1) Exportar dados do ChatGPT
ChatGPT → *Settings* → *Data Controls* → **Export Data**.  
Recebes um `.zip` (ex.: `2025-06-03.zip`).

---

## 2) Gerar o “Diário” em Markdown (1 ficheiro por conversa)

**Script**: `chatgpt_diario_v3.py`  
- Descompacta o `.zip` e cria `.md` individuais + `INDEX.md`.  
- Usa títulos, datas, e grava **hashtags** (inicialmente “genéricas”).

**Configurar Caminhos:**
```
ZIP_PATH   = r"L:\cgp-diary-agent\2025-06-03.zip"
OUTPUT_DIR = r"L:\cgp-diary-agent\ChatGPT_Diario_v3"
```

**Run:**
```bash
python C:\cgp-diary-agent\chatgpt_diario_v3.py
```

**Resultado:**  
`C:\cgp-diary-agent\ChatGPT_Diario_v3\` com milhares de `.md` + `INDEX.md`.

> **Performance:** a pasta temporária `temp_extract` não é necessária no vault → move-a para fora antes de abrir no Obsidian.

---

## 3) Abrir no Obsidian como novo Vault
Obsidian → **Open folder as vault** → `ChatGPT_Diario_v3`.  
Se custar a indexar:
- remove `temp_extract`,  
- desativa temporariamente Graph view / Backlinks,  
- (opcional) divide por anos.

---

## 4) Tags semânticas (multilingue) — o “pulo do gato”

**Ficheiro de temas**: `topics.json` (editável).  
**Script**: `semantic_tag_vault.py`
- Gera embeddings (`paraphrase-multilingual-MiniLM-L12-v2`),  
- Classifica cada nota em **1–3 temas** (ex.: `#filosofia #tria #trading`),  
- Substitui/insere a linha de tags logo abaixo da data,  
- Cria `TagIndex.md` (contagem por tema).

**Run:**
```bash
python L:\cgp-diary-agent\semantic_tag_vault.py
```

**Saída esperada:**
```
✅ Notas processadas: 1847 | Atualizadas: 1847
📘 Índice criado em: ...\TagIndex.md
```

**Efeito:** no **Graph View**, aparecem **clusters por cor** (agrupamento por `tag:`).

---

## 5) Ligações reais entre notas (rede viva)

**Script**: `semantic_link_vault.py`
- Lê tags de cada nota,  
- Encontra outras notas que partilham ≥ 1 tag,  
- Adiciona no fim do ficheiro:
```
---
**Ligações relacionadas**
[[YYYY-MM-DD - Título 1]]
[[YYYY-MM-DD - Título 2]]
...
```
- Evita duplicados (substitui bloco antigo).

**Run:**
```bash
python L:\cgp-diary-agent\semantic_link_vault.py
```

No Obsidian: reabre → Graph view → aumenta *link thickness/force* → verás linhas entre notas e comunidades bem definidas.

---

## 6) Limpar notas “pesadas” (Crash Fix)

Alguns `.md` traziam blocos JSON/asset (`"asset_pointer"`, `sediment://…`) que congelam o Obsidian.  
**Script**: `clean_sediment_md.py`
- Procura e remove esses blocos,  
- Normaliza linhas em branco,  
- Guarda backup `.bak`.

**Run:**
```bash
python L:\cgp-diary-agent\clean_sediment_md.py
```

**Saída:**
```
✅ Processados: N | Limpados: M + backups .bak onde alterou.
```

---

## 7) Afinar o Graph View

**Groups (cores por tag):**  
`tag:#filosofia, tag:#trading, tag:#tria, tag:#espiritualidade, tag:#ia, …`

**Filtros úteis:**
- “Display unlinked files” → off (para focar na rede),  
- “Min link length” → reduzir “ruído”,  
- “Repulsion/Center force” → ajustar layout.  
**Local Graph** de uma nota → ver vizinhança semântica.

---

## 😎 Atualizações futuras (pipeline incremental)

Quando tiveres novo `.zip`:
1. Corre `chatgpt_diario_v3.py` para gerar novas notas (podes usar a mesma pasta).  
2. Corre `semantic_tag_vault.py` — ele substitui/insere a linha de tags (**idempotente**).  
3. Corre `semantic_link_vault.py` — renova o bloco “**Ligações relacionadas**” (**idempotente**).  
4. (Se houver crash em novos ficheiros) corre `clean_sediment_md.py`.

---

## 9) Problemas que resolvemos (útil)

- **Paths/aspas:** `r"C:\..."` (evitar `""...""`).  
- **JSON como lista:** adaptámos o parser.  
- **Conteúdos multimodais (dicts):** extração segura (`text`, `caption`).  
- **Datas ISO vs timestamp:** detetor duplo.  
- **Caracteres ilegais em nomes:** `safe_filename` (remove/trunca).  
- **Tabs vs spaces:** scripts finais só com 4 espaços.  
- **Obsidian indexing lento:** mover `temp_extract`, dividir por ano, desativar plugins pesados.  
- **Search/Replace no Obsidian:** a UI mudou → optámos por scripts.  
- **Arquivos “sediment”:** limpeza automática com backup.

---

## Estrutura final de scripts 

- `chatgpt_diario_v3.py` → cria os `.md` a partir do `.zip`.  
- `topics.json` → dicionário de temas semânticos (editas livremente).  
- `semantic_tag_vault.py` → escreve hashtags de temas nas notas + `TagIndex.md`.  
- `semantic_link_vault.py` → adiciona `[[ligações]]` entre notas relacionadas.  
- `clean_sediment_md.py` → remove blocos problemáticos (`asset_pointer`/`sediment://`).

