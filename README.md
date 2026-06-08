# GreenOps AI: Xebia’s Unified Carbon Reduction Dashboard

GreenOps AI is a cloud sustainability and ESG platform designed to transition cloud infrastructure tracking from a manual, reactive model to a proactive, data-driven sustainability architecture. It integrates cloud consumption data, forecasts carbon emissions using Machine Learning, and provides actionable optimization recommendations to reduce carbon footprints and optimize spend.

## Project Structure
```text
greenops-ai-dashboard/
├── data/              # Raw and enriched usage datasets, visualization charts
├── model/             # Time-series forecasting and regression models
├── api/               # FastAPI backend services
├── dashboard/         # Streamlit/React interactive frontend
└── README.md          # Documentation and Concept Checks
```

---

## Concept Checks

### 🚀 Hurdle 0: Orientation & Azure Setup

#### 1. What is a Resource Group in Azure, and why do we use one?
An Azure **Resource Group** is a logical container that groups related Azure services and resources (such as Virtual Machines, Storage Accounts, databases, and App Services) for a specific solution. We use resource groups to:
- **Unified Management**: Easily deploy, update, or delete all resources in a single action (lifecyle management).
- **Access Control**: Apply Role-Based Access Control (RBAC) at the resource group level, inheriting permissions down to all resources inside.
- **Billing & Cost Tracking**: Group billing data together to monitor the cost of specific environments (like production, staging, development).

#### 2. What is the difference between a virtual environment and a global Python installation?
- **Global Python Installation**: Installs packages system-wide, shared by all users and all projects. This frequently causes version conflicts (e.g., project A needing pandas `1.x` and project B needing pandas `2.x`).
- **Virtual Environment (`venv`)**: Creates an isolated directory with its own copy of the Python interpreter, pip package manager, and a local site-packages folder. Every dependency installed here is isolated, ensuring project reproducibility and preventing conflicts.

#### 3. Why is version control important from Day 1 of a project?
Version control (like Git) is essential from day one to:
- **Traceability**: Maintain a complete chronological history of code changes, enabling teams to understand *why* and *when* lines of code were modified.
- **Rollback Safety**: Revert to previous working states instantly if new code introduces breaking bugs.
- **Collaboration**: Prevent developers from overwriting each other's work by merging changes through branches and pull requests.
- **Professional Discipline**: Keep experimental features separate from the stable codebase.

### 📊 Hurdle 1: Dataset & Carbon Baseline

#### 1. What does CO2e mean and why is it used as the standard unit for carbon accounting?
**CO2e (Carbon Dioxide Equivalent)** is a standard metric used to compare the emissions from various greenhouse gases (such as methane, nitrous oxide, and fluorinated gases) on the basis of their **Global Warming Potential (GWP)** over a specific timeframe (usually 100 years).
- **Why it is used**: Different gases trap different amounts of heat. For instance, methane is about 28 times more potent than CO2 over 100 years. Expressing all emissions in CO2e provides a single, standardized unit for carbon accounting, enabling unified comparisons, tracking, and reporting.

#### 2. Why is it important to separate emission factors by resource type rather than using a single flat rate?
Cloud infrastructure components use energy differently:
- **Compute (VMs/CPUs)**: Draws highly dynamic power directly proportional to CPU utilization.
- **Storage**: Consumes power constantly to keep disks spinning (HDDs) or powered (SSDs), regardless of access rate.
- **Data Transfer (Networking)**: Uses power in bursts across switches and fiber-optic routers to transmit packets.
Using a single flat rate would obscure the root causes of emissions, leading to inaccurate metrics and ineffective optimization decisions (e.g., trying to optimize storage when networking is the major driver).

#### 3. What is the most carbon-intensive service type in your dataset?
Based on our data processing script:
- **Networking** is the most carbon-intensive service type, producing **7.5127 kg CO2e** (46.3% of total emissions).
- This is followed closely by **VM (Compute)** at **5.8584 kg CO2e** (36.1%).

#### Baseline Carbon Performance Metrics (Results)
- **Total Ingested Rows (after null cleaning)**: 1,603 rows (17 incomplete rows cleaned)
- **Total Cloud Spend**: $4,742.20 USD
- **Average Daily Spend**: $12.99 USD
- **Total Carbon Footprint**: **16.2243 kg CO2e**

##### Carbon Emissions by Service Type:
- **Networking**: 7.5127 kg CO2e (46.3%)
- **VM (Compute)**: 5.8584 kg CO2e (36.1%)
- **Storage**: 1.4923 kg CO2e (9.2%)
- **Database**: 1.3609 kg CO2e (8.4%)

##### Carbon Emissions by Region:
- **eastus**: 7.9587 kg CO2e (49.1%)
- **westeurope**: 4.9390 kg CO2e (30.4%)
- **southeastasia**: 3.3266 kg CO2e (20.5%)

##### Carbon Emissions by Team:
- **Engineering**: 6.3078 kg CO2e (38.9%)
- **Data**: 4.0950 kg CO2e (25.2%)
- **DevOps**: 3.5145 kg CO2e (21.7%)
- **QA**: 2.3070 kg CO2e (14.2%)

### 🗄️ Hurdle 2: Data Storage on Azure

#### 1. What is the difference between Azure Blob Storage and Azure SQL Database? When would you choose each?
- **Azure Blob Storage**: An object storage solution designed to store massive amounts of unstructured data (such as CSVs, JSONs, images, videos, backups, and machine learning model weights).
  - *When to choose*: When you need cost-effective, high-throughput storage for files, batch processing data sources, logs, or backups.
- **Azure SQL Database**: A fully managed relational database (RDBMS) that supports structured data, relational tables, SQL queries, index optimization, and transactional consistency (ACID compliance).
  - *When to choose*: When your data requires complex relational integrity, transactions, real-time query joins, and strict data typing (e.g., e-commerce orders, user profiles).

#### 2. What is LRS replication and what are its limitations vs GRS?
- **LRS (Locally Redundant Storage)**: Replicates your data synchronously three times within a single physical datacenter in the primary region.
  - *Limitation*: If the entire datacenter facility experiences a major disaster (such as a fire, flood, or power grid failure), LRS data could be permanently lost or inaccessible.
- **GRS (Geo-Redundant Storage)**: Replicates your data synchronously three times in the primary region, and then replicates it asynchronously to a secondary region (hundreds of miles away) for disaster recovery.
  - *Comparison*: GRS protects against complete regional disasters, offering much higher durability at a higher cost.

#### 3. Why is it a security risk to hardcode a connection string in source code?
- **Maintenance Overhead**: Rotating keys (a security best practice) or moving between environments (Dev, Staging, Production) becomes difficult and error-prone because it requires changes to the codebase itself rather than configuration changes.

### 🌐 Hurdle 4: Dashboard & API Layer

#### 1. What is REST and why is it the standard for building APIs?
**REST (Representational State Transfer)** is an architectural style for designing networked applications. It utilizes stateless client-server communication and standard HTTP protocols (GET, POST, PUT, DELETE).
- **Why it is standard**: REST relies on standard HTTP methods, making it extremely lightweight, language-agnostic, scalable, and simple to implement and test. It promotes decoupling of client and server.

#### 2. What is the difference between a GET and a POST request? Which would you use to submit new billing data?
- **GET Request**: Used to retrieve data from a server. Data is sent in the URL path or query parameters, and requests should be idempotent (meaning they do not alter the server state).
- **POST Request**: Used to send data to the server to create/update a resource. Data is packaged in the request body (not the URL), allowing large amounts of data to be transmitted securely.
- **Selection**: To submit new billing data, you would use a **POST** request since it alters the database state (creates new records) and transmits sensitive data in the request body.

#### 3. Why run the API and dashboard as two separate processes rather than one combined script?
Running them as separate processes conforms to the **Separation of Concerns** principle:
- **Scalability**: You can scale the FastAPI backend independently from the frontend dashboard (e.g., run multiple backend API replicas behind a load balancer).
- **Modularity**: You can build other frontends (e.g., mobile apps, CLI tools, enterprise portals) that consume the exact same FastAPI endpoints without modifying any data logic.
- **Resilience**: A frontend crash (e.g., rendering error) does not crash the backend metrics ingestion pipeline.

---

### ☁️ Hurdle 5: Deploy to Azure & Shift-Left Green Score

#### 1. What is the 'Shift-Left' principle in DevOps, and how does the Green Score apply it to sustainability?
- **Shift-Left**: The practice of moving tasks (such as security testing, code quality checks, and performance optimization) to the earliest phases of the software development lifecycle (SDLC) rather than waiting until deployment or post-production.
- **Applying to Green Score**: By computing a "Green Score" sustainability rating based on historical/predicted emissions, the system acts as a CI/CD build gate. A project scoring F triggers a warning or soft block *during* the build phase, forcing developers to optimize resource usage *before* code reaches production.

#### 2. What is Azure App Service and how is it different from running on a VM (IaaS)?
- **Azure App Service (PaaS - Platform as a Service)**: A fully managed service for hosting web applications and REST APIs. Azure handles OS patching, scaling, hardware provisioning, load balancing, and network configuration automatically.
- **Azure VM (IaaS - Infrastructure as a Service)**: Gives you raw access to a virtual machine where you must configure the operating system, web server (Nginx/IIS), security updates, firewall rules, and runtime environments yourself. PaaS allows you to focus purely on code rather than infrastructure management.

#### 3. If a project scores F, what specific infrastructure changes would you recommend first?
1. **Rightsizing VMs**: Check CPU/RAM utilization telemetry. Scale down over-provisioned VMs to match actual workloads (e.g., switching from `D4s_v5` to `D2s_v5`).
2. **Switching Regions**: Migrate resources to regions with lower carbon intensity (cheaper, renewable energy grids like `westeurope` instead of coal-heavy grids).
3. **Storage Tiering**: Move archival data from active hot storage to cool or archive storage tiers.
4. **Auto-scaling Policies**: Configure auto-scalers to shut down non-production environments (QA, Dev) during off-business hours (nights and weekends).



