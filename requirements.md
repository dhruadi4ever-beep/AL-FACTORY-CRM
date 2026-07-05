# ARYAN LACE ERP — Requirements

## 1. Product Purpose
ARYAN LACE is a factory-management ERP for a lace manufacturing unit. The system must support day-to-day factory operations, production control, inventory movement, workforce tracking, and decision support in a way that can be extended as business rules evolve.

## 2. Guiding Principles
- The system must follow the 17 business chapters provided by the business owner. Each chapter will refine behavior and rules.
- The data model must be completely dynamic. Machine count, item count, employee count, and job worker count are unlimited and managed through master data.
- No hardcoded business values are allowed for operational entities such as machines, items, worker types, process stages, or stock categories.
- Every inventory movement must be recorded in a stock ledger for auditability.
- AI support is advisory only and must never execute transactions.

## 3. Functional Requirements
### 3.1 Master Data
The system must support configurable master data for:
- Items and item families
- Machines and machine groups
- Employees and roles
- Job workers and job-worker groups
- Suppliers and customers
- Locations, departments, units, and cost centers
- Process definitions and routing steps

Each master entity must support dynamic attributes and metadata so the business can extend the model without code changes.

### 3.2 Production Management
The system must support:
- Production planning and work-order creation
- Process-stage execution and tracking
- Machine allocation and downtime tracking
- Job-worker assignment and performance tracking
- Output confirmation, rejections, and quality exceptions

### 3.3 Inventory and Stock
The system must support:
- Goods receipt, issue, transfer, return, and adjustment transactions
- Quantity and value tracking
- Full audit trail via stock ledger transactions
- Batch or lot-level visibility where needed
- Inventory reconciliation and exception reporting

### 3.4 Mobile Experience
The Android application must provide:
- A dashboard with KPI cards, health score, and charts
- A Smart Factory Assistant panel for recommendations and alerts
- Quick actions for common daily operations
- Fast access to production and inventory workflows

### 3.5 Intelligence Layer
The system must include an intelligent advisory layer that:
- Reviews historical patterns and operational data
- Produces recommendations for operations, inventory, and productivity
- Never writes transactions directly
- Presents recommendations as advisory insights only

## 4. Non-Functional Requirements
- Secure authentication and role-based access control
- Auditability for all business events
- Clear API contracts and maintainable backend services
- Scalable architecture for future modules and users
- Testability, observability, and deployment readiness

## 5. Initial Delivery Scope
The first implementation milestone will establish:
- Project structure and documentation
- Backend API foundation
- PostgreSQL-based persistence model
- Dynamic master-data design
- Android app shell and dashboard skeleton

## 6. Clarification Gate
The implementation will remain aligned to the business chapters as they are provided. Once the initial documents are reviewed, clarifying questions will be asked before any production code is written.
