# Skills Repository

[![skills.sh](https://skills.sh/b/rhoribe/skills)](https://skills.sh/rhoribe/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Coleção de **Agent Skills** abertas e modulares compatíveis com o ecossistema [skills.sh](https://skills.sh), **Google Antigravity**, **Claude Code**, **Cursor**, **GitHub Copilot**, **Windsurf**, **Gemini CLI** e outros assistentes de IA.

---

## ⚡ Instalação Rápida (via `skills.sh`)

Instale todas as skills deste repositório com um único comando utilizando a CLI oficial `skills`:

```bash
# Instalação no projeto local:
npx skills add rhoribe/skills

# Instalação global (disponível em todos os seus projetos e agentes):
npx skills add rhoribe/skills -g

# Instalar apenas a skill os-update:
npx skills add rhoribe/skills --skill os-update

# Instalar para agentes específicos (ex: Claude Code, Antigravity e Cursor):
npx skills add rhoribe/skills --agent claude-code antigravity cursor
```

---

## 📦 Skills Disponíveis

| Skill | Descrição | Plataformas |
|---|---|---|
| [`os-update`](./skills/os-update/SKILL.md) | Fluxo automatizado e seguro (*dry-run first*) para inspecionar, preparar e aplicar atualizações de SO e pacotes com diagnósticos de segurança e alerta de reboot. | **Linux** (Debian, Ubuntu, Fedora, RHEL, Arch, openSUSE, Alpine, Flatpak, Snap) & **macOS** (`softwareupdate`, Homebrew, MAS) |

---

## 🛠️ Arquitetura da Skill `os-update`

A skill implementa a especificação oficial de **Agent Skills** ([agentskills.io](https://agentskills.io)) com divulgação progressiva (*progressive disclosure*):

```text
skills/os-update/
├── SKILL.md                          # Instruções para o agente (5 fases de execução)
├── scripts/                          # Utilitários portáveis (POSIX/Bash)
│   ├── detect_os.sh                  # Detecta SO, arquitetura, kernel, espaço em disco e gerenciadores
│   ├── check_updates.sh              # Inspeciona atualizações pendentes (modo somente leitura / dry-run)
│   └── update_system.sh              # Aplica atualizações com suporte a --security-only, --scope e --clean
└── references/                       # Manuais técnicos e runbooks especializados
    ├── linux.md                      # Detalhes para APT, DNF, Pacman, Zypper, APK, Snap e Flatpak
    ├── macos.md                      # Detalhes para softwareupdate, Homebrew, MAS e snapshots APFS
    ├── safety-and-rollback.md        # Checklists pré-execução, proteção de /boot e snapshots
    └── troubleshooting.md            # Recuperação de locks presos, chaves e dependências quebradas
```

---

## 🚀 Como Publicar no `skills.sh`

Este repositório já está configurado com o [`skills.sh.json`](./skills.sh.json) e a estrutura exigida pelo indexador do **skills.sh**.

### Passo a passo para publicação:

1. **Commit e Push para o GitHub**:
   ```bash
   git add .
   git commit -m "feat: add os-update skill and skills.sh configuration"
   git push -u origin main
   ```

2. **Garantir que o repositório é Público**:
   - Acesse o repositório no GitHub: `https://github.com/rhoribe/skills`
   - Certifique-se de que a visibilidade está configurada como **Public**.

3. **Adicionar Tópicos (Topics) no GitHub**:
   No menu lateral direito do seu repositório no GitHub ("About" ⚙️), adicione as seguintes tags para acelerar a descoberta e categorização:
   - `skills-sh`
   - `agent-skills`
   - `ai-agents`
   - `antigravity`
   - `os-update`
   - `sysadmin`

4. **Indexação Automática**:
   O `skills.sh` indexa o repositório assim que a primeira instalação ocorrer via CLI ou ao ser consultado:
   ```bash
   npx skills add rhoribe/skills -l
   ```
   A página do repositório ficará disponível publicamente em:
   `https://skills.sh/rhoribe/skills`

---

## 💻 Uso Local e Desenvolvimento

### No Google Antigravity
O repositório inclui [`.agents/skills.json`](./.agents/skills.json), garantindo carregamento imediato quando aberto como workspace:
```json
{
  "entries": [
    { "path": "skills" }
  ]
}
```

### Execução Manual dos Scripts (Sem Agente)
```bash
# Detectar ambiente:
./skills/os-update/scripts/detect_os.sh

# Checar atualizações pendentes:
./skills/os-update/scripts/check_updates.sh

# Simular atualização (dry-run):
./skills/os-update/scripts/update_system.sh --dry-run

# Executar atualização com limpeza de cache:
./skills/os-update/scripts/update_system.sh --clean
```

---

## 📄 Licença

Distribuído sob licença [MIT](./LICENSE).
