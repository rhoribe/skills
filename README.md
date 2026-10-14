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

# Instalar uma skill específica:
npx skills add rhoribe/skills --skill iac-topology
npx skills add rhoribe/skills --skill os-update

# Instalar para agentes específicos (ex: Claude Code, Antigravity e Cursor):
npx skills add rhoribe/skills --agent claude-code antigravity cursor
```

---

## 📦 Skills Disponíveis

| Skill | Descrição | Formatos & Plataformas |
|---|---|---|
| [`iac-topology`](./skills/iac-topology/SKILL.md) | Gera diagramas e desenhos de topologia de arquitetura em nuvem diretamente de código IaC (**Terraform**, **CloudFormation**, **Azure Bicep**, **Ansible**, **Kubernetes**), exportando para **Excalidraw**, **Draw.io** e **Mermaid**. | **Excalidraw** (`.excalidraw`), **Draw.io** (`.drawio`), **Mermaid** (`.mmd`) / Multiplataforma |
| [`os-update`](./skills/os-update/SKILL.md) | Fluxo automatizado e seguro (*dry-run first*) para inspecionar, preparar e aplicar atualizações de SO e pacotes com diagnósticos de segurança e alerta de reboot. | **Linux** (Debian, Ubuntu, Fedora, RHEL, Arch, openSUSE, Alpine, Flatpak, Snap) & **macOS** (`softwareupdate`, Homebrew, MAS) |

---

## 🛠️ Arquitetura das Skills

As skills implementam a especificação oficial de **Agent Skills** ([agentskills.io](https://agentskills.io)) com divulgação progressiva (*progressive disclosure*):

### 1. `iac-topology`
```text
skills/iac-topology/
├── SKILL.md                          # Instruções para o agente (5 fases de execução)
├── scripts/                          # Utilitários de parsing e renderização de diagramas
│   ├── parse_iac.py                  # Parser universal (Terraform, CloudFormation, Bicep, Ansible, K8s)
│   ├── generate_excalidraw.py        # Gerador nativo Excalidraw v2 com auto-layout e paletas por nuvem
│   ├── generate_drawio.py            # Gerador nativo Draw.io / mxGraphModel com swimlanes e nós estilizados
│   ├── generate_mermaid.py           # Gerador de flowcharts Mermaid para preview imediato em Markdown
│   └── iac_topology.sh               # CLI unificada para geração de diagramas
└── references/                       # Guias de parsing e especificações de formato
    ├── terraform.md                  # HCL, módulos, recursos e terraform show -json
    ├── cloudformation.md             # Templates YAML/JSON, Ref, Fn::GetAtt e DependsOn
    ├── bicep.md                      # Recursos Bicep, módulos e ARM templates
    ├── ansible.md                    # Módulos cloud para AWS, Azure, GCP e Docker
    ├── excalidraw-spec.md            # Especificação do schema JSON do Excalidraw
    └── drawio-spec.md                # Especificação XML do mxGraphModel do Draw.io
```

### 2. `os-update`
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

### Execução dos Utilitários da Skill `iac-topology`
```bash
# Gerar todos os formatos (Excalidraw, Draw.io e Mermaid) para um diretório Terraform:
./skills/iac-topology/scripts/iac_topology.sh ./meu-projeto/terraform/ --output-dir ./diagramas

# Gerar arquivo Excalidraw a partir de um template CloudFormation:
./skills/iac-topology/scripts/iac_topology.sh template.yaml --format excalidraw

# Gerar arquivo Draw.io (.drawio) a partir de um arquivo Azure Bicep:
./skills/iac-topology/scripts/iac_topology.sh main.bicep --format drawio --title "Arquitetura Azure"

# Gerar diagrama a partir de playbooks Ansible:
./skills/iac-topology/scripts/iac_topology.sh playbook.yml --format all
```

### Execução dos Utilitários da Skill `os-update`
```bash
# Detectar ambiente:
./skills/os-update/scripts/detect_os.sh

# Checar atualizações pendentes:
./skills/os-update/scripts/check_updates.sh

# Simular atualização (dry-run):
./skills/os-update/scripts/update_system.sh --dry-run
```

---

## 🚀 Como Publicar no `skills.sh`

Este repositório já está configurado com o [`skills.sh.json`](./skills.sh.json) e a estrutura exigida pelo indexador do **skills.sh**.

### Passo a passo para publicação:

1. **Commit e Push para o GitHub**:
   ```bash
   git add .
   git commit -m "feat: add iac-topology skill for Excalidraw and Draw.io diagrams"
   git push -u origin main
   ```

2. **Garantir que o repositório é Público**:
   - Acesse o repositório no GitHub: `https://github.com/rhoribe/skills`
   - Certifique-se de que a visibilidade está configurada como **Public**.

3. **Adicionar Tópicos (Topics) no GitHub**:
   No menu lateral direito do seu repositório no GitHub ("About" ⚙️), adicione as seguintes tags:
   - `skills-sh`
   - `agent-skills`
   - `iac`
   - `terraform`
   - `cloudformation`
   - `bicep`
   - `ansible`
   - `excalidraw`
   - `drawio`
   - `os-update`

---

## 📄 Licença

Distribuído sob licença [MIT](./LICENSE).
