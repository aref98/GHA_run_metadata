# GHARuns_Collector

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![Tests](https://github.com/aref98/GHA_run_metadata/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/aref98/GHA_run_metadata/actions/workflows/ci.yml)
[![Dependabot](https://badgen.net/badge/Dependabot/enabled/green?icon=dependabot)](https://dependabot.com/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Last Commit](https://img.shields.io/github/last-commit/aref98/GHA_run_metadata)](https://github.com/aref98/GHA_run_metadata/commits/main)

A fault-tolerant, large-scale data extraction pipeline designed to collect massive datasets of GitHub Actions workflow runs, jobs, steps, and annotations. This tool was developed for the **ICSME 2026 Data Track** to support empirical research on CI/CD reliability and maintainability.




```mermaid
flowchart TD
    %% Base Node Styling: Smaller boxes, bigger/bolder fonts
    classDef core fill:#f3f4f6,stroke:#9e9e9e,stroke-width:2px,font-size:14px,font-weight:bold,padding:5px;
    classDef phaseA fill:#bbdefb,stroke:#0288d1,stroke-width:2px,font-size:14px,font-weight:bold,padding:5px;
    classDef phaseB fill:#c8e6c9,stroke:#388e3c,stroke-width:2px,font-size:14px,font-weight:bold,padding:5px;
    classDef phaseC fill:#ffe082,stroke:#f57c00,stroke-width:2px,font-size:14px,font-weight:bold,padding:5px;
    classDef decision fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,font-size:14px,font-weight:bold,padding:5px;
    classDef endpoint fill:#374151,color:#fff,stroke:#374151,stroke-width:2px,font-size:16px,font-weight:bold,padding:8px;

    %% Subgraph Background Styling (Semi-transparent with matching borders)
    classDef bgA fill:#e3f2fd,stroke:#0288d1,stroke-width:2px,stroke-dasharray: 5 5;
    classDef bgB fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,stroke-dasharray: 5 5;
    classDef bgC fill:#fff8e1,stroke:#f57c00,stroke-width:2px,stroke-dasharray: 5 5;
    classDef bgTransparent fill:none,stroke:none;

    %% Initial Steps
    A(["Start"]) --> B["Load Repository List"]
    B --> C["Resolve Time Window\nfrom state file"]
    C --> D{"Within grace\nperiod?"}
    D -- Yes --> Z(["End"])
    D -- No --> E{"Phase A\nalready complete?"}

    %% PHASE A: REST Discovery
    subgraph TitleA [**Phase A — REST Discovery**]
        subgraph BoxA [ ]
            F["Query REST API\nfor completed runs"]
            G["Filter & save runs\nto runs.jsonl"]
            H["Enqueue check suite IDs\ninto GraphQL buffer"]
            I{"GraphQL buffer\nfull?"}
            
            F --> G --> H --> I
        end
    end

    E -- No --> F
    I -- No, next repo --> F

    %% PHASE B: GraphQL Enrichment
    subgraph TitleB [**Phase B — GraphQL Enrichment**]
        subgraph BoxB [ ]
            K["Batch-query jobs & steps\nvia GraphQL API"]
            L{"Run exceeds\nGraphQL page limits?"}
            M["Write jobs & steps\nto details.jsonl"]
            N["Add to massive\nruns buffer"]
            O{"More runs\nin GraphQL buffer?"}
            
            K --> L
            L -- No --> M --> O
            L -- Yes --> N --> O
            O -- Yes --> K
        end
    end

    I -- Yes --> K
    E -- Yes --> K

    %% PHASE C & FINALIZATION
    subgraph TitleC [**Phase C — REST Cleanup & State Save**]
        subgraph BoxC [ ]
            P{"Any massive runs\nin buffer?"}
            Q["Fetch full jobs & steps\nvia REST API"]
            R["Write to details.jsonl"]
            S["Save report &\ncheckpoint state"]
            T{"More windows\nto process?"}

            P -- Yes --> Q --> R --> S
            P -- No --> S
            S --> T
        end
    end

    O -- No --> P
    T -- Yes --> C
    T -- No --> Z

    %% Apply Base Classes
    class A,Z endpoint;
    class B,C,S core;
    class D,E,I,L,O,P,T decision;
    class F,G,H phaseA;
    class K,M,N phaseB;
    class Q,R phaseC;

    %% Apply Subgraph Styles
    class TitleA,TitleB,TitleC bgTransparent;
    class BoxA bgA;
    class BoxB bgB;
    class BoxC bgC;

```
