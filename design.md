# ARYAN LACE ERP — Design

## 1. Architectural Overview
The system is implemented as a layered, modular platform with three main parts:
- Android client for operations and dashboards
- Backend API for business logic, persistence, and integrations
- PostgreSQL database for transactional and master data

The design remains configuration-driven so business rules can evolve without hardcoded behavior.

## 1A. Chapter 1, Chapter 2, Chapter 3, Chapter 4, Chapter 5, Chapter 6, Chapter 7, and Chapter 8 Implementation Scope
Chapter 1 establishes the operational philosophy for the ERP. Chapter 2 adds the master-data foundation that later modules depend on. Chapter 3 introduces production planning and machine assignment. Chapter 4 adds automatic forecasting based on running hours and item standards. Chapter 5 adds actual production recording, inventory updates, locking rules, and validation warnings. Chapter 6 adds job-work assignment, bunch-based transfer, partial completion, and finished-goods conversion flow. Chapter 7 adds packing and parcel management for dispatch-ready grouping of PCS. Chapter 8 adds stage-wise inventory control, stock ledger tracking, and stock adjustments.

The implementation now reflects these principles:
- dynamic master data support
- active/inactive lifecycle for master records
- unique coding and searchable master records
- historical traceability via change history
- event-based operational tracking
- dashboard and assistant alert support for factory oversight
- advisory guidance without transaction execution

## 2. Core Architecture Principles
- Separation of concerns across presentation, application services, domain services, and persistence
- Dependency inversion so business logic is independent from transport details
- Dynamic master-data model instead of rigid, hardcoded entity structures
- Event-driven transaction handling for stock movement and operational updates
- Advisory AI integration as a read-only decision support service

## 3. Recommended Technology Stack
### Backend
- Python with FastAPI
- SQLAlchemy for ORM and database access
- Pydantic for schema validation
- Alembic for migrations
- PostgreSQL as the primary database
- Redis optional for caching and background jobs

### Android App
- Kotlin
- Jetpack Compose for UI
- Retrofit for API calls
- Hilt for dependency injection
- Room optional for local caching and offline support

### Intelligence Layer
- Gemini API client service
- A read-only recommendation engine that consumes historical and current data
- Recommendation results stored as advisory records for traceability

## 4. Domain Design Strategy
### 4.1 Dynamic Master Data Model
The core data model uses configurable master entities rather than fixed code-level assumptions. Examples:
- Generic master records for items, machines, employees, job workers, bobbins, and other business entities
- Dynamic attributes stored as metadata
- Type-based classification for business objects
- Rule-driven configuration for process steps and validations

This keeps the platform flexible while still supporting strong transactional behavior.

### 4.2 Transactional Core
The system treats operational events as first-class transactional records. Every important factory activity can be recorded as an event with:
- event type
- reference context
- payload details
- timestamp
- actor reference

This supports the Chapter 1 requirement for preserving historical visibility and operational traceability.

## 5. Suggested Backend Module Structure
- auth: user authentication and authorization
- masters: dynamic master-data management
- production: work orders, routing, execution, output, and quality events
- inventory: receipt, issue, transfer, adjustment, and stock ledger
- reporting: dashboards, KPIs, and operational analytics
- intelligence: advisory recommendations and AI integration
- shared: common utilities, base models, and infrastructure concerns

## 6. Suggested API Design
The API should expose resource-oriented endpoints for:
- masters
- production orders
- machine and labor allocation
- inventory transactions
- dashboard KPIs
- advisory recommendations

Use versioned endpoints and clear response schemas. Prefer consistent pagination, filtering, and error handling.

## 7. Database Design Direction
The database will include:
- Users and roles
- Dynamic master entities and metadata
- Production transaction tables
- Inventory transaction and stock ledger tables
- Rule configuration tables
- Advisory and audit tables

JSONB fields can be used for dynamic attributes where appropriate, while core transactional tables remain strongly typed for consistency and reporting.

## 8. Android App Structure
The Android app will be organized around:
- dashboard screen
- operations screen
- inventory screen
- production screen
- assistant screen
- quick actions module

The UI will favor simple, mobile-first workflows optimized for factory-floor use.

## 9. Deployment and Operations
- Containerized backend and database services
- Environment-based configuration
- Logging, metrics, and health checks
- CI/CD pipeline for backend and app releases
- Separate environments for development, staging, and production

## 10. Evolution Path
This design establishes the foundation for the first milestone. The detailed rules from each business chapter will be translated into configuration and domain rules rather than hardcoded logic.
