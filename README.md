<div align="center">

# MercadoVoz

### Natural-language business records with human confirmation

MercadoVoz is a system designed for small merchants in **Cuenca, Ecuador** who need a fast way to record sales, expenses, receivables and payments using everyday language.

The key rule is simple:

> **No financial operation is persisted until the user reviews and confirms it.**

<br>

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

<br>

![Status](https://img.shields.io/badge/Status-Private_Pilot-2563EB?style=flat-square)
![Core](https://img.shields.io/badge/Core_Engine-Working-16A34A?style=flat-square)
![Market Validation](https://img.shields.io/badge/Market_Validation-Pending-D97706?style=flat-square)

</div>

---

## Overview

Small merchants often manage their business using:

- notebooks;
- memory;
- calculators;
- WhatsApp messages;
- informal notes.

This can lead to:

- unregistered sales;
- forgotten expenses;
- difficult-to-track customer debt;
- incorrect payment records;
- confusion between personal and business money;
- poor visibility into who owes what.

MercadoVoz tries to preserve the simplicity of natural language while converting it into structured business data.

A merchant can write:

```text
María quedó debiendo 12
```

MercadoVoz can interpret it as:

```text
Operation: RECEIVABLE
Customer: María
Amount: $12
```

But that operation is **not stored immediately**.

The system first shows the interpretation to the user:

```text
Receivable

Customer: María
Amount: $12

[ Confirm ]
[ Correct ]
[ Cancel ]
```

Only after confirmation is the operation persisted.

---

## Core Principle

MercadoVoz follows a safety-first rule:

> **If the system is not sufficiently certain, it asks for clarification or abstains. It does not invent a transaction.**

For example:

```text
me pagó todo lo de ayer
```

does not contain enough information to safely determine:

- who paid;
- what debt is being referenced;
- what amount should be registered.

MercadoVoz can use controlled context when available, but it should not fabricate missing financial information.

---

## Main Operations

The current core focuses on four financial operations.

### SALE

A completed sale.

```text
vendí 3 libras de tomate a 2 dólares
```

Possible structured result:

```json
{
  "operation": "SALE",
  "product": "tomate",
  "quantity": 3,
  "unit": "libra",
  "unit_price": 2,
  "total": 6
}
```

---

### EXPENSE

A business expense.

```text
gasté 5 en transporte
```

Possible result:

```json
{
  "operation": "EXPENSE",
  "description": "transporte",
  "amount": 5
}
```

---

### RECEIVABLE

Money that a customer now owes to the business.

```text
Carlos quedó debiendo 10
```

Possible result:

```json
{
  "operation": "RECEIVABLE",
  "customer": "Carlos",
  "amount": 10
}
```

---

### PAYMENT_RECEIVED

A payment against an existing receivable.

```text
Carlos me abonó 5
```

Possible result:

```json
{
  "operation": "PAYMENT_RECEIVED",
  "customer": "Carlos",
  "amount": 5
}
```

Inventory and purchasing have been explored, but they are not currently part of the primary core.

---

## How It Works

```text
Natural-language input
        │
        ▼
Normalization
        │
        ▼
Interpretation Engine
        │
        ▼
Safety Layer
        │
        ▼
Context Layer
        │
        ▼
Operation Proposal
        │
        ▼
Human Confirmation
        │
        ▼
Persistence
        │
        ▼
Audit Trail
```

MercadoVoz is therefore not simply a text parser.

It is an interpretation pipeline designed specifically around financial safety.

---

## Interpretation Engine

The Interpretation Engine attempts to extract information such as:

- intent;
- operation type;
- amount;
- quantity;
- product;
- customer;
- unit;
- unit price.

Example:

```text
vendí 5 libras de tomate a 2 cada una
```

can produce:

```json
{
  "operation": "SALE",
  "product": "tomate",
  "quantity": 5,
  "unit": "libra",
  "unit_price": 2,
  "total": 10
}
```

The current engine is primarily **deterministic**.

It does not require an LLM for the core interpretation path.

That is intentional.

For financial operations, deterministic behavior provides several advantages:

- reproducibility;
- predictable cost;
- low latency;
- explainability;
- precise automated tests;
- easier debugging;
- lower risk of hallucinated financial data.

LLMs may become useful for specific auxiliary tasks, but the financial core should remain controlled.

---

## Safety Layer

The Safety Layer is one of the most important components in MercadoVoz.

Its purpose is to detect potentially unsafe interpretations before an operation reaches persistence.

For example:

```text
hoy hice como 40
```

should not automatically become:

```text
SALE = $40
```

because:

```text
como 40
```

expresses approximation.

Another example:

```text
saqué cinco para la casa
```

could describe a personal withdrawal rather than a business expense.

Registering it directly as:

```text
EXPENSE = $5
```

could corrupt the business records.

The safety system therefore considers cases such as:

- approximate monetary values;
- unit price vs total price;
- coordinated quantities;
- compound operations;
- personal money vs business money;
- debt creation vs debt status;
- missing customers;
- missing context;
- ambiguous references;
- multiple possible interpretations.

---

## Semantic Safety Example

Consider these two sentences:

```text
Juan quedó debiendo 10
```

and:

```text
Juan todavía debe 10
```

They look similar, but they represent very different states.

The first may represent the creation of a new receivable:

```text
RECEIVABLE +$10
```

The second may simply describe an already existing debt.

A naive system could register another $10 receivable and duplicate the customer's debt.

MercadoVoz is designed to avoid exactly this type of financial mistake.

---

## Context Layer

People naturally speak using context.

Example:

```text
María debe 20
```

followed by:

```text
me abonó cinco
```

The second sentence does not mention María.

MercadoVoz can maintain controlled contextual information such as:

```text
active_customer = María
active_receivable = 20
```

and propose:

```json
{
  "operation": "PAYMENT_RECEIVED",
  "customer": "María",
  "amount": 5,
  "remaining_balance": 15
}
```

However, the proposal still requires user confirmation.

Context is not treated as infinite conversational memory.

Each contextual reference can include:

```text
source
created_at
expires_at
invalidation_rules
```

This limits how long implicit information can influence financial operations.

---

## Confirmation Engine

Financial operations move through explicit states.

```text
PROPOSED
CONFIRMED
CORRECTED
REJECTED
CANCELLED
```

Example:

```text
MercadoVoz understood:

SALE

Product: Tomato
Quantity: 5 lb
Total: $10

[ Confirm ]
[ Correct ]
[ Cancel ]
```

The system therefore operates using a **human-in-the-loop** model.

Interpretation is automated.

Financial commitment is not.

---

## Correction Engine

If an interpretation is incorrect, the user should not need to repeat the entire operation.

Example:

```text
MercadoVoz:
Amount: $5
```

User:

```text
no, eran seis
```

The correction engine can update the relevant field:

```text
Amount: $6
```

without rebuilding the complete operation manually.

Fields that can be corrected include:

- operation type;
- amount;
- quantity;
- product;
- customer;
- unit;
- unit price.

---

## Audit Trail

Every financial operation can maintain traceability.

The audit record may contain:

```text
original_text
normalized_text
engine_version
context_used
fields_extracted
warnings
safety_rules_triggered
initial_proposal
corrections
confirmation
final_operation
```

This makes it possible to answer questions such as:

> Why did MercadoVoz store this transaction in this way?

For a system that handles financial records, this level of explainability is important.

---

## Architecture

```text
┌─────────────────────────────┐
│           Client            │
│      Browser / Mobile       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Next.js / React        │
│        TypeScript           │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          FastAPI            │
│          Python             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Interpretation Engine    │
├─────────────────────────────┤
│       Safety Layer          │
│       Context Layer         │
│    Confirmation Engine      │
│      Correction Engine      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         SQLite WAL          │
└─────────────────────────────┘
```

---

## Technology Stack

### Frontend

![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

The frontend is responsible for:

- user input;
- interpretation preview;
- correction flow;
- operation confirmation;
- history;
- consent;
- responsive interface.

The UI is designed with a **mobile-first** approach because the target users are small merchants who are likely to interact with the system from a phone.

---

### Backend

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

FastAPI connects the frontend with the interpretation engine.

Example API surface:

```text
POST /interpret
POST /confirm
POST /correct
GET  /history
```

FastAPI provides:

- schema validation;
- automatic API documentation;
- typed request models;
- lightweight asynchronous APIs;
- simple integration with Python logic.

---

### Database

![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

The current pilot uses:

```text
SQLite + WAL
```

WAL stands for:

```text
Write-Ahead Logging
```

It improves SQLite's behavior when reads and writes occur concurrently.

SQLite is currently appropriate because MercadoVoz is still in pilot stage and does not yet require distributed database infrastructure.

The current architecture assumes a controlled backend deployment rather than many independent application instances writing simultaneously.

---

## Infrastructure

The pilot infrastructure is prepared around an Oracle Cloud virtual machine.

```text
Oracle Cloud
US East — Ashburn

Ampere A1 Flex
2 OCPU
12 GB RAM
Ubuntu 24.04 ARM64
50 GB storage
```

Expected deployment architecture:

```text
                    Internet
                       │
                       ▼
                 ┌───────────┐
                 │   Nginx   │
                 └─────┬─────┘
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
     Next.js :3000             FastAPI :8000
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                    SQLite
```

Nginx can route:

```text
/
```

to Next.js and:

```text
/api/
```

to FastAPI.

---

## Process Management

The infrastructure uses:

### PM2

For managing the Next.js process.

```bash
pm2 start ...
```

PM2 allows the application to continue running after the SSH session is closed and can restart the process after failures.

### systemd

FastAPI is intended to run as a Linux service managed by `systemd`.

This provides:

- automatic startup;
- restart behavior;
- logs;
- operating-system-level process management.

---

## Server Security

The server configuration includes:

![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

Security measures include:

- SSH key authentication;
- UFW firewall;
- Fail2ban;
- controlled inbound ports;
- Nginx reverse proxy;
- future HTTPS termination.

The goal is to expose only the services that need to be reachable publicly.

---

## Repository Structure

MercadoVoz uses a monorepo-style structure.

```text
mercadovoz/
│
├── apps/
│   ├── web/
│   └── api/
│
├── engine/
│
├── tests/
│
├── research/
│
├── docs/
│
├── scripts/
│
├── data/
│
├── .github/
│
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── AGENTS.md
```

### apps/web

Next.js frontend.

### apps/api

FastAPI application layer.

### engine

Core natural-language interpretation and financial safety logic.

### tests

Automated tests and evaluation cases.

### research

Research artifacts used during development and domain exploration.

### docs

Technical and product documentation.

### scripts

Development, evaluation and operational utilities.

### data

Controlled local data and non-sensitive development artifacts.

---

## Git Workflow

Primary branches:

```text
main
develop
```

Development branches follow patterns such as:

```text
feature/*
fix/*
docs/*
chore/*
hotfix/*
```

`main` should remain deployable.

`develop` is used as the primary integration branch during active development.

---

## Evaluation

MercadoVoz was not evaluated only with a small set of manually chosen examples.

Different dataset categories have been used during development:

```text
SYNTHETIC
WEB_DERIVED
WEB_DERIVED_MULTISOURCE
REAL_DEVELOPMENT
REAL_HELDOUT
```

An external benchmark was also created using research focused primarily on the language and commercial behavior of merchants in **Cuenca and Ecuador**.

The benchmark contains:

```text
240 external cases
```

These cases cover areas such as:

- sales;
- expenses;
- receivables;
- payments;
- context;
- compound operations;
- ambiguous financial language;
- commercial vocabulary;
- unsafe interpretations.

The corresponding technical evaluation reached:

```text
TECHNICAL_STATUS = TECHNICAL_GO
```

without known critical monetary violations in that evaluation.

However:

```text
TECHNICAL_GO ≠ MARKET_VALIDATED
```

Passing technical benchmarks does not demonstrate that real merchants will find the product useful or easy to use.

Real-world validation is still required.

---

## Project Status

| Component | Status |
|---|---|
| Idea | Complete |
| Research | Complete |
| Proof of Concept | Complete |
| Deterministic Parser | Complete |
| Safety Engine | Complete |
| Context Layer | Complete |
| Confirmation Engine | Complete |
| Correction Engine | Complete |
| Core Engine | Complete |
| External Benchmark | Complete |
| Text MVP | Complete |
| Private Pilot Preparation | Complete |
| GitHub Repository | In progress |
| Oracle Cloud Deployment | Next |
| First Real Pilot | Pending |
| Voice Interface | Pending |
| Market Validation | Pending |

---

## Current Stage

MercadoVoz has passed an important technical milestone:

```text
text
  ↓
interpretation
  ↓
safety
  ↓
context
  ↓
proposal
  ↓
confirmation
  ↓
structured operation
```

The next major question is no longer only:

> Can the engine interpret commercial language?

It is:

> Will real merchants actually prefer this interaction model over their current habits?

That requires real-world testing.

---

## Why Text Before Voice?

Voice is part of the long-term vision, but it is intentionally not the current priority.

The future flow could look like:

```text
Microphone
    │
    ▼
Speech-to-text
    │
    ▼
MercadoVoz
    │
    ▼
Interpretation
    │
    ▼
Confirmation
```

However, adding speech recognition does not solve a bad interaction model.

The project first needs to validate that:

```text
natural language → safe financial operation
```

is genuinely useful to merchants.

If real users demonstrate that typing is inconvenient, voice becomes a strong next step.

---

## Design Philosophy

MercadoVoz is built around several principles.

### Human confirmation over silent automation

Financial operations should not be silently generated from uncertain language.

### Explainability over black-box behavior

The system should be able to explain how it interpreted an operation.

### Determinism where money is involved

Core financial logic should remain reproducible and testable.

### Context with boundaries

Context is useful, but it should have clear origin, scope and expiration.

### Abstention is a valid result

Not understanding a sentence safely is better than inventing a transaction.

### Real-world validation over benchmark confidence

Technical tests can reduce risk.

They cannot replace real users.

---

## Example End-to-End Flow

Input:

```text
Juan me abonó cinco
```

The system may resolve the controlled context:

```text
active_customer = Juan
active_receivable = $20
```

Then create a proposal:

```text
Operation: PAYMENT_RECEIVED
Customer: Juan
Amount: $5
Previous balance: $20
New balance: $15
```

The user sees:

```text
Juan paid $5

Remaining debt: $15

[ Confirm ]
[ Correct ]
[ Cancel ]
```

Only after:

```text
CONFIRMED
```

is the final financial operation persisted.

---

## Long-Term Vision

The goal is to make business record keeping feel closer to normal conversation than traditional accounting software.

A merchant could eventually say or write:

```text
vendí cinco libras de papa a dos dólares
```

```text
gasté tres en pasajes
```

```text
María quedó debiendo diez
```

```text
María abonó cinco
```

and MercadoVoz could generate a daily view such as:

```text
Sales
$145

Expenses
$18

Receivables
$37

Payments received
$22
```

without requiring the merchant to learn a complex accounting interface.

---

## What MercadoVoz Is Not

MercadoVoz is currently **not**:

- a complete accounting platform;
- a tax system;
- an ERP;
- a replacement for professional accounting;
- a market-validated commercial product;
- a voice-first system yet;
- an autonomous financial agent.

It is currently an experimental business-record system focused on:

> **safe transformation of natural language into user-confirmed structured financial records.**

---

## Roadmap

```text
Core interpretation engine
        ✅
        │
Safety and ambiguity detection
        ✅
        │
Controlled context
        ✅
        │
Confirmation / correction
        ✅
        │
External evaluation
        ✅
        │
Text MVP
        ✅
        │
Oracle Cloud deployment
        🔜
        │
Real merchant pilot
        ⏳
        │
Usability validation
        ⏳
        │
Market validation
        ⏳
        │
Voice input
        ⏳
```

---

## Contributing

MercadoVoz is currently in an early development and validation stage.

Before contributing, please read:

```text
CONTRIBUTING.md
```

For security-related information:

```text
SECURITY.md
```

Development instructions and repository conventions may also be documented in:

```text
AGENTS.md
```

---

## Security

Do not report security vulnerabilities through public GitHub issues.

Please follow the process documented in:

```text
SECURITY.md
```

Financial correctness and data integrity are treated as first-class concerns in this project.

---

## Author

**David Mendez**

Full-Stack Developer  
Universidad Católica de Cuenca  
Cuenca, Ecuador

[![GitHub](https://img.shields.io/badge/GitHub-lildavicho-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lildavicho)

---

<div align="center">

### MercadoVoz

**Natural language for business records, without inventing financial operations.**

<sub>Built for experimentation, validation and real-world learning with small merchants.</sub>

</div>
