# Product Requirements Document (PRD)
## Smart Labor Cost Estimator (AI RAG System)

### 1. Product Overview
**Objective:** Develop a smart, offline-first AI system that leverages historical POS data and Retrieval-Augmented Generation (RAG) to provide service advisors with accurate, consistent, and context-aware labor hour and cost estimates.
**Target User:** Internal Service Advisors (starting as a single-user system).
**Primary Vehicle Focus:** Small Hyundai trucks (HD45, HD72, H100).

### 2. Core Architecture & Tech Stack
The system is designed for high reliability, fast local execution, and a clean user experience without relying on active internet connections or cloud latency.

* **Frontend:** Next.js
    * Landscape-optimized layout for desktop/tablet use at the advisor desk.
    * Clean, highly responsive UI for rapid query input and result scanning.
* **Backend:** Python (FastAPI)
    * Handles the RAG logic, query processing, and communication between the frontend and the vector database.
* **Vector Database (AI Memory):** ChromaDB or FAISS (Local)
    * Stores embeddings of historical jobs, cross-referenced with vehicle models and component categories.
* **Data Ingestion:** Static
    * V1 will operate on the current comprehensive CSV export. Automatic continuous ingestion is out of scope for the initial build.

### 3. Key Features & Workflows

#### 3.1. Localization & Language Settings
* **Interface Language:** Toggleable between Arabic and English via the settings menu. 
* **AI Response Language:** Independent toggle allowing the advisor to set the AI's output language (Arabic or English) regardless of the UI language, fully supporting RTL layouts for Arabic readability.

#### 3.2. Smart Query Engine
* **Natural Language Input:** Advisors can type queries using common Libyan workshop slang (e.g., *"HD45 - كشف صالة وتغيير مسمار ميزان"*).
* **Range Estimations:** The AI outputs a confidence interval based on historical data percentiles (e.g., "Estimated Labor: 1.5 to 2.5 Hours") rather than a single rigid number.
* **Transparent Outlier Handling:** The frontend displays the standard calculated estimate but includes a collapsible "Details" section revealing anomalies (e.g., *"Notice: 1 historical record for this job took 6.0 hours"*).

#### 3.3. Hybrid Dictionary Management
A dedicated module to bridge local terminology with standardized automotive categories (Engine, Transmission, Suspension, etc.).
* **Proactive Management (CRUD):** An interface allowing the advisor to manually add, edit, or delete terms (e.g., mapping "تكهيات" to Valve Lifters or "جبة" to Cylinder Block).
* **Reactive Learning (Pending Review Inbox):** If the AI encounters an unknown term during a query, it flags it and routes it to an inbox. The advisor can later map this new term to a standard category, instantly updating the vector database's understanding for future queries.

#### 3.4. Internal PDF Export
* **Simple Reporting:** A one-click export generating a basic, internally formatted PDF.
* **Content:** Contains the vehicle details, queried jobs, estimated hour ranges, calculated costs, and historical outlier notes. It is designed purely as an advisor reference sheet, not a polished customer-facing invoice.

### 4. Data Processing & Vectorization Strategy
* **Standardization Layer:** Raw historical CSV data will be cleaned using the baseline dictionary before vectorization.
* **Embedding Focus:** The vectorization process must heavily weight the vehicle `Model` to prevent cross-contamination of labor times (e.g., ensuring a Corolla brake job does not influence an HD45 brake job estimate).
* **Core Metrics:** The primary extracted values for calculation are `QTY` (Labor Hours) and `Price` (Hourly Rate), grouped by standard job categories.

### 5. Future Considerations (Post V1)
* Implementation of Role-Based Access Control (RBAC) for multiple service advisors.
* Migration to a cloud-based PostgreSQL (`pgvector`) setup for multi-branch syncing.
* Direct API integration with ERP systems (e.g., Odoo) to automatically push estimated quotes into official work orders.