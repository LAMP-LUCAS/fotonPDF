# 🕸️ Grafo de Relacionamentos da Documentação

Este documento usa **Mermaid** para visualizar as conexões entre os documentos do projeto.

## Visão Geral - Hierarquia

```mermaid
graph TD
    README[📄 README.md<br/>Entrada Principal]
    MAP[🗺️ MAP.md<br/>Centro de Navegação]
    
    README --> MAP
    README --> LLM[🧠 LLM_CONTEXT.md]
    
    MAP --> ARCH[🏗️ ARCHITECTURE.md]
    MAP --> DEV[🛠️ DEVELOPMENT.md]
    MAP --> BUS[💰 BUSINESS.md]
    MAP --> ROAD[🚀 ROADMAP.md]
    MAP --> GUIDES[📖 Guides]
    MAP --> MODULES[🧩 Modules]
    
    GUIDES --> NEW_OP[➕ NEW_OPERATION.md]
    GUIDES --> PLUGIN[🔌 PLUGIN_SYSTEM.md]
    GUIDES --> OS_INT[🖥️ OS_INTEGRATION.md]
    
    MODULES --> MOD_INDEX[📦 INDEX.md]
    
    CONTRIB[🤝 CONTRIBUTING.md]
    
    style README fill:#4CAF50
    style MAP fill:#2196F3
    style LLM fill:#FF9800
```

## Fluxo de Uso para Diferentes Personas

### 👨‍💻 Desenvolvedor Novo

```mermaid
journey
    title Jornada de Onboarding
    section Dia 1
      Ler README: 5: Dev
      Explorar MAP: 5: Dev
      Setup Ambiente (DEVELOPMENT): 4: Dev
    section Dia 2
      Entender Arquitetura: 4: Dev
      Ler CONTRIBUTING: 5: Dev
      Escolher Issue: 3: Dev
    section Dia 3
      Seguir NEW_OPERATION: 5: Dev
      Escrever Código: 4: Dev
      Submeter PR: 5: Dev
```

### 🤖 CodeAssistant (LLM)

```mermaid
flowchart LR
    START[Tarefa Recebida]
    START --> CONTEXT[Ler LLM_CONTEXT.md]
    CONTEXT --> CHECK{Tipo de tarefa?}
    
    CHECK -->|Nova Feature| ARCH[ARCHITECTURE]
    CHECK -->|Bug Fix| DEV[DEVELOPMENT]
    CHECK -->|Plugin| PLUGIN[PLUGIN_SYSTEM]
    CHECK -->|OS Integration| OS[OS_INTEGRATION]
    
    ARCH --> CODE[Escrever Código]
    DEV --> CODE
    PLUGIN --> CODE
    OS --> CODE
    
    CODE --> TEST[Executar Testes]
    TEST --> DONE[✅ Concluído]
```

### 📊 Product Owner / Stakeholder

```mermaid
graph LR
    README --> BUS[BUSINESS.md<br/>Modelo Econômico]
    README --> ROAD[ROADMAP.md<br/>Sprints]
    
    BUS --> MVP[Foco MVP]
    BUS --> FUTURE[Monetização Futura]
    
    ROAD --> PHASE1[Fase 1: Fundação]
    ROAD --> PHASE2[Fase 2: Funcionalidade]
    ROAD --> PHASE3[Fase 3: Ecossistema]
    
    style BUS fill:#FFC107
    style ROAD fill:#9C27B0
```

## Dependências entre Módulos de Código

```mermaid
graph TB
    subgraph "Camada de Domínio"
        DOMAIN[domain/<br/>Entidades + Portas]
    end
    
    subgraph "Camada de Aplicação"
        APP[application/<br/>Casos de Uso]
    end
    
    subgraph "Camada de Infraestrutura"
        INFRA[infrastructure/<br/>Adapters]
    end
    
    subgraph "Camada de Interface"
        UI[interfaces/<br/>UI + CLI + Context Menu]
    end
    
    UI --> APP
    APP --> DOMAIN
    INFRA --> DOMAIN
    UI --> INFRA
    
    style DOMAIN fill:#E8F5E9
    style APP fill:#E3F2FD
    style INFRA fill:#FFF3E0
    style UI fill:#F3E5F5
```

## Sistema de Navegação (Obsidian Graph)

```mermaid
mindmap
  root((fotonPDF))
    📘 Início
      README
      MAP
      INDEX
    🏗️ Engenharia
      ARCHITECTURE
      DEVELOPMENT
      Modules
        Core PDF
        UI Framework
        System Integration
    📚 Tutoriais
      NEW_OPERATION
      PLUGIN_SYSTEM
      OS_INTEGRATION
    💼 Produto
      BUSINESS
      ROADMAP
    🤝 Comunidade
      CONTRIBUTING
      LLM_CONTEXT
```

## Como Usar Este Grafo

1. **No Obsidian:** Use o plugin "Obsidian Mermaid" para renderizar os diagramas.
2. **No GitHub:** Os diagramas Mermaid renderizam automaticamente.
3. **Localmente:** Use `mermaid-cli` ou ferramentas online.

---

[[MAP|Voltar ao Mapa]] | [[INDEX|Ver Índice Completo]]
