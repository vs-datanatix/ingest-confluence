---
applyTo: "**"
---
<!-- AUTO-GENERATED FROM CONFLUENCE — DO NOT EDIT MANUALLY -->
<!-- Source: https://datanatix.atlassian.net/spaces/PS/pages/196997/Development+Standards | Last synced: 2026-07-31 12:03:15 UTC -->

# Development Standards

**Audience:** Data Engineers, Data Scientists, Analytics Engineers, BI Developers

* + No transformations; preserve source format
  + Partition by ingestion date and source system
  + Implement watermark columns (ingestion timestamp)
  + Use Delta table format exclusively
* **Silver Layer:** Cleansed, deduplicated, conformed data

  + Apply business rules and validation logic
  + Enforce referential integrity constraints
  + Partition by business keys and date ranges
  + Implement slowly changing dimensions (SCD Type 2 for history)
  + Use clustered column store for fact tables >10GB
* **Gold Layer:** Business-ready aggregated data

  + Pre-aggregated fact tables and marts
  + Time-series denormalized for reporting
  + Optimize for known query patterns
  + Implement access controls at table level

### 1.2 Table Design & Naming

* **Naming Convention:**

  + Format: `[layer]_[domain]_[object]` (e.g., `silver_finance_transactions`)
  + Use snake\_case for all identifiers
  + Prefix fact tables with `fact_`, dimensions with `dim_`
  + Avoid reserved keywords; use descriptive names
* **Column Standards:**

  + Use meaningful, business-oriented column names
  + Data type conversions at Silver layer (enforce string → date/numeric)
  + Surrogate keys for all dimensions (bigint, starting at 1)
  + Natural keys retained for traceability
  + Nullable columns documented; default to NOT NULL
  + Implement change-tracking columns: `dbt_updated_at`, `dbt_valid_from`, `dbt_valid_to`

### 1.3 Performance Optimization

* **Clustered Columnstore Index (CCI):**

  + Apply to fact tables; row groups >1GB per partition
  + Disable on dimensions <100MB or high-churn transactional tables
* **Liquid Clustering:**

  + Cluster on common join/filter columns (e.g., customer\_id, date)
  + Ideal for tables 100GB–10TB with skewed distributions
  + Reduces data skew during aggregation queries
* **Partitioning Strategy:**

  + Date-based partitions (monthly/quarterly) for time-series data
  + Geographic or tenant-based for multi-tenant workloads
  + Avoid over-partitioning (<100 GB per partition)
  + Purge old partitions per retention policy
* **File Layout:**

  + Target 128MB–1GB per file; avoid small-file proliferation
  + Run `OPTIMIZE TABLE` monthly post-ingestion
  + Use `ZORDER BY` for multi-column filter optimization
  + Monitor file counts via Fabric Monitoring Hub

---

## 2. Data Quality & Validation Standards

### 2.1 Quality Checks

* **Schema Validation:**

  + Assert column presence, data types, nullability on ingestion
  + Fail pipeline if schema drift detected (unplanned changes)
  + Document expected schema versions in metadata
* **Data Validation:**

  + Row counts: Assert ±5% variance from source baseline
  + Null checks: Enforce NOT NULL on key columns
  + Referential integrity: FK relationships at Silver layer
  + Business rules: Negative amounts, future dates, invalid codes → quarantine
  + Duplicates: Identify and deduplicate at Bronze → Silver
* **Implementation:**

  + Use Fabric Dataflow validation rules
  + Implement dbt tests (`not_null`, `unique`, `relationships`, `accepted_values`)
  + Log all failures to `audit_log` table with timestamp and source
  + Alert on >5% data quality failures

### 2.2 Data Lineage & Metadata

* **Lineage Tracking:**

  + Capture source → Bronze → Silver → Gold transformations
  + Document column-level lineage for critical metrics
  + Use dbt docs for automated lineage graphs
  + Integrate with Purview for enterprise governance
* **Metadata Management:**

  + Table description: Business purpose, refresh cadence, owner
  + Column descriptions: Business definition, valid ranges, examples
  + Data classification: Public/Internal/Confidential
  + Retention policy: Archive/delete schedule
  + SLA: Acceptable latency, availability targets

---

## 3. Dataflow & ETL Standards

### 3.1 Dataflow Design

* **Modularity:**

  + One logical transformation per dataflow (avoid monoliths >50 steps)
  + Reuse common transformations as dataflow templates
  + Keep joins/unions under 10 tables per step
* **Transformation Logic:**

  + Perform aggregations at the lowest layer where data is ready (push-down)
  + Avoid client-side aggregation; use window functions or pre-built marts
  + Use conditional logic sparingly; document business rules inline
  + Implement idempotent transformations (safe re-runs)
* **Error Handling:**

  + Define fallback rules for missing dimensions (unknown keys)
  + Quarantine failed records in dedicated error table
  + Log error details: timestamp, source row ID, reason, attempted value
  + Implement circuit breaker for >10% failure rate

### 3.2 Refresh & Scheduling

* **Incremental vs. Full Refresh:**

  + Incremental: Tables >1GB; use watermark/timestamp for delta detection
  + Full: Small reference tables, dimensions <500MB, monthly recalc needed
  + Document refresh frequency in table metadata (hourly/daily/weekly)
  + Monitor refresh SLA in Fabric Monitoring Hub
* **Scheduling:**

  + Stagger workloads to avoid peak capacity hours
  + Use UTC timestamps exclusively
  + Implement retry logic (3 attempts, exponential backoff)
  + Alert on refresh failures within 30 minutes

---

## 4. Data Security & Access Control

### 4.1 Access Control Strategy

* **Workspace RBAC:**

  + Admin: Data platform team only
  + Member: Analytics engineers, approved data engineers
  + Contributor: Analysts creating reports within sandbox workspaces
  + Viewer: Consumer access to curated reports/dashboards only
* **Row-Level Security (RLS):**

  + Implement for multi-tenant data (e.g., regional sales)
  + Use dax roles scoped to user/role dimensions
  + Test RLS with non-admin users quarterly
  + Document active RLS rules in metadata

### 4.2 Data Classification & Masking

* **Classification Levels:**

  + Public: Aggregated, no PII
  + Internal: Operational, no customer data
  + Confidential: Raw PII (names, emails, phone)
  + Restricted: Financial, healthcare, government IDs
* **Masking Rules:**

  + PII columns: Apply sensitivity labels (Confidential)
  + Mask in development/UAT environments (hashing or truncation)
  + Implement Copilot restrictions via "Approved for Copilot" allowlist
  + Review data loss prevention (DLP) policies quarterly

### 4.3 Audit & Compliance

* **Change Tracking:**

  + Enable Delta table change data capture (CDC) for regulated tables
  + Log all schema changes and data deletions
  + Retain audit logs for 7 years (legal/compliance requirement)
* **Certification:**

  + Mark Gold layer tables as "Certified" post-validation
  + Require data owner sign-off before certification
  + Document SLA and support contacts

---

## 5. Data Modeling Standards

### 5.1 Star Schema Design

* **Fact Tables:**

  + Contain surrogate keys + measures (amounts, counts, ratios)
  + Partition by date; size partitions 100MB–1GB
  + Denormalize for performance if >1B rows
  + Use additive measures (no semi-additive ratios in raw fact)
* **Dimension Tables:**

  + Implement Type 2 SCD for historical tracking (valid\_from/valid\_to)
  + Limit to <100 columns per dimension
  + Flag obsolete records; soft-delete over hard-delete
  + Maintain role-playing dimensions (e.g., `dim_date` reused for order/ship dates)

### 5.2 Handling Slowly Changing Dimensions (SCD)

* **Type 2 (Versioned):**

  + Use for dimensions with historical importance (customers, products, employees)
  + Add `valid_from` (start of record) and `valid_to` (end, NULL for current)
  + Create separate current/history split at Gold layer for query performance
  + Archive old versions to read-only storage after 2 years
* **Type 1 (Overwrite):**

  + Use for reference data (currency codes, region mappings)
  + No history required; simple update

### 5.3 Aggregate & Materialized Views

* **Pre-aggregated Lake Views:**

  + Create materialized mart tables for known reporting queries
  + Aggregate at: daily, monthly, quarterly levels
  + Update on schedule aligned to source refresh
  + Document aggregation logic and drill-down paths

---

## 6. Dataset & Semantic Model Standards

### 6.1 Semantic Layer Design

* **Entity Model:**

  + Hub-and-spoke topology for multi-source consolidation
  + Central fact table linked to dimension shortcuts
  + Minimize ambiguous relationships; use explicit shortcuts
  + Avoid circular dependencies between tables
* **Measures & DAX:**

  + Define all business metrics as explicit DAX measures (not implicit sums)
  + Use CALCULATE() for context filtering; avoid FILTER for performance
  + Implement time intelligence (YTD, YoY growth) in semantic layer
  + Cache frequently used measures; mark volatile measures with `CACHE OFF`
  + Code review DAX for complexity >5 function nesting levels

### 6.2 Relationships & Cardinality

* **Relationship Rules:**

  + Set to "Active" only if filtering is frequent; inactive for alternate paths
  + Enforce many-to-one cardinality; flag one-to-many for review
  + Use role-playing dimensions with explicit measure definitions
  + Test cross-filter direction in preview (avoid bidirectional unless necessary)
* **Performance Considerations:**

  + Monitor relationship cardinality in Query Store
  + Denormalize many-to-many relationships into bridge tables
  + Use `TREATAS()` for complex dimension mappings

### 6.3 Dataset Refresh & Incremental Load

* **Refresh Settings:**

  + Schedule daily/hourly aligned to dataflow cadence
  + Enable DirectQuery only for small reference dimensions
  + Use import mode for fact tables >5GB
  + Implement incremental refresh for partition pruning (save storage/time)
* **Monitoring:**

  + Log refresh duration and row count changes
  + Alert if refresh exceeds 120% of baseline duration
  + Track semantic model size; flag >10GB uncompressed

---

## 7. Reporting & BI Standards

### 7.1 Report Development

* **Page Structure:**

  + Limit to 6–8 visuals per page (cognitive load, performance)
  + Implement drill-through and drill-down navigation
  + Use consistent color palette (brand-approved, accessibility compliance)
  + Title each visual and page with clear, business language
* **Interactions & Filtering:**

  + Default to cross-filtering; document exceptions
  + Implement page-level filters (date range, department)
  + Use slicers for self-service; avoid complex DAX filtering
  + Disable interactions for unrelated visuals

### 7.2 Visual Best Practices

* **Chart Selection:**

  + Bars: Comparisons across categories
  + Lines: Trends over time
  + Scatter: Correlation/distribution analysis
  + Maps: Geographic/spatial patterns
  + Avoid pie charts; use stacked bar if comparing parts of whole
* **Formatting:**

  + Number format: 2 decimals for currency, 0 for counts
  + Conditional formatting: Highlight outliers >3σ from mean
  + Font size: 11pt minimum (accessibility)
  + Data labels: Show only on top N categories (reduce clutter)

### 7.3 Report Performance & Optimization

* **Query Performance:**

  + Pre-filter large datasets at semantic layer (e.g., last 12 months)
  + Avoid visuals with >100K data points (use aggregations instead)
  + Monitor query duration in Performance Analyzer (<5 seconds target)
  + Cache drillthrough datasets; disable real-time refresh if not required
* **Publishing & Distribution:**

  + Use app-based distribution for governed consumers
  + Implement share-to-Teams for ad-hoc analysis
  + Set row-level security (RLS) roles before publishing
  + Document report purpose, owner, and refresh cadence

---

## 8. Documentation & Code Standards

### 8.1 Inline Documentation

* **Dataflow Comments:**

  + Explain non-obvious transformation logic
  + Reference source documentation (Jira tickets, requirements)
  + Note known limitations or workarounds
* **DAX Documentation:**

  + Comment complex measures with business definition
  + Document assumptions (e.g., "assumes no NULL values in Date column")
  + Include refresh date for static measures
* **Metadata in Tabular Model:**

  + Table descriptions: Source, owner, update frequency
  + Column descriptions: Business definition, units, valid range
  + Measure descriptions: Calculation method, SLA implications

### 8.2 Version Control

* **dbt Project Structure:**

  + Track Fabric SQL notebooks and dataflow definitions in Git
  + Branch per feature; merge via pull request with code review
  + Tag stable releases (v1.0.0, v1.1.0)
  + Document breaking changes in CHANGELOG
* **Fabric Workspace Deployment:**

  + Use Git integration for semantic models (PBIP format)
  + Separate DEV/UAT/PROD workspaces with read-only production
  + Tag production deployments in Git with date and version

---

## 9. Testing & Validation Standards

### 9.1 Testing Layers

* **Unit Tests (dbt):**

  + `not_null`: Assert critical columns have no nulls
  + `unique`: Surrogate keys, natural keys (PK/FK integrity)
  + `relationships`: FK constraints (e.g., order.customer\_id references customer.id)
  + `accepted_values`: Enum columns (status, region codes)
  + Coverage: ≥80% of columns in Silver/Gold layers
* **Integration Tests:**

  + Row count variance <±5% from source baseline
  + Duplicate detection post-dedup (expect 0)
  + Join cardinality validation (many-to-one)
  + Test with recent data (last 7 days); run nightly
* **Semantic Model Tests:**

  + Measure validation: YTD vs. year-to-date calculation in Excel
  + Relationship cardinality: Verify many-to-one cardinality
  + RLS effectiveness: Test with user roles (cross-user data isolation)
  + Query performance: Benchmark top 10 queries; alert if >150% baseline

### 9.2 UAT & Sign-Off

* **Test Data Requirements:**

  + Use anonymized production-representative data
  + Include edge cases (nulls, zeros, negative values, future dates)
  + Document test data lineage and retention
* **Sign-Off Process:**

  + Data owner validation: Row counts, sample spot-checks
  + Business analyst validation: Logic correctness, measure alignment
  + Performance sign-off: Load times, refresh duration acceptable
  + Document findings in JIRA; resolve blockers before go-live

---

## 10. Monitoring, Logging & Observability

### 10.1 Dataflow & Lakehouse Monitoring

* **Refresh Metrics:**

  + Monitor duration, row count, error rate per dataflow
  + Alert on >120% baseline duration or >5% failure rate
  + Track storage growth (flag >20% spike month-over-month)
* **Query Performance:**

  + Log top 10 slow queries (>30 sec) daily
  + Track Query Store for missing indexes, parameter sensitivity
  + Alert on CPU/memory pressure in capacity utilization
* **Audit Logging:**

  + Table access: Who, when, query type (read/write)
  + Schema changes: Column adds, data type changes, deletes
  + Failed validations: Record count variances, PK violations
  + Retention: 7 years for regulated data; 1 year for standard

### 10.2 Alerting & Runbooks

* **Alert Thresholds:**

  + Refresh SLA breach: Page on-call immediately
  + Data quality failure: Escalate within 1 hour
  + Query timeout: Log and notify BI team; investigate if >3 occurrences/day
  + Storage quota: Alert at 80%, 95% thresholds
* **Incident Response:**

  + Create runbooks for common issues (failed refresh, missing data, performance regression)
  + Log root cause analysis (RCA) in Confluence
  + Post-mortems for critical incidents; document lessons learned
  + Monthly SLA review with stakeholders

---

## 11. Change Management & Deployment

### 11.1 Deployment Workflow

* **Dev → UAT → Prod:**

  + DEV: Individual developer workspace; test schema changes
  + UAT: Integration environment; data owner + analyst validation
  + PROD: Read-only for consumers; changes via Git pull request + approval
  + Rollback plan: Tag previous version; document rollback procedure
* **Change Approval:**

  + Schema changes: Data architect + owner sign-off
  + Metric changes: Analytics lead + business owner approval
  + Performance changes: Data engineer + BI lead review
  + Emergency changes: Incident commander authorization + post-incident review

### 11.2 Release Management

* **Versioning:**

  + Semantic versioning (major.minor.patch)
  + Major: Breaking changes to data model
  + Minor: New tables/measures (backward compatible)
  + Patch: Bug fixes, performance improvements
  + Tag releases in Git with date, author, change summary
* **Communication:**

  + Release notes published 24 hours before deployment
  + Downtime window announced in Teams channel
  + Post-deployment validation checklist (health checks, data freshness)
  + Stakeholder confirmation before closing change ticket

---

## 12. Cost Optimization & Governance

### 12.1 Capacity Management

* **Workspace Allocation:**

  + Audit unused workspaces quarterly; archive/consolidate
  + Monitor per-workspace query volume and storage
  + Set auto-scale triggers (>80% capacity utilization)
  + Monthly cost allocation to business units
* **Query Optimization:**

  + Identify top 10 cost-driving queries (highest duration × frequency)
  + Implement caching for repeated queries
  + Push filtering to dataflow layer (reduce semantic model scans)
  + Deprecate unused reports after 6 months inactivity

### 12.2 Governance & Compliance

* **Data Governance Council:**

  + Meet quarterly; review data incidents, policy changes
  + Approve new data sources and retention policies
  + Resolve data ownership disputes
  + Track metrics: Certified tables %, data quality score, SLA adherence
* **Policy Review:**

  + Annual audit of access controls, RLS rules, data classifications
  + Compliance validation (GDPR, SOX, industry-specific)
  + Incident post-mortems; update policies based on findings

---

## Appendix: Checklists

### Bronze → Silver Transformation Checklist

* Source data profiled; schema documented
* Deduplication logic applied; duplicates logged
* Data type conversions (strings → date/numeric)
* Null handling defined per column
* SCD logic applied (Type 1 or Type 2)
* dbt tests added (not\_null, unique, relationships)
* Row count variance <±5%
* Table partitioned by date or business key
* Clustered columnstore enabled for fact tables

### Gold Layer Publishing Checklist

* Measure definitions documented in DAX
* Pre-aggregation strategy validated
* Partitioning strategy optimized
* File optimization completed (OPTIMIZE TABLE)
* Security/RLS rules implemented
* Dataset refresh schedule confirmed
* Data owner sign-off obtained
* Table marked as "Certified" post-validation

### Report Publishing Checklist

* Visuals tested with actual data; no errors/nulls
* Performance Analyzer confirms <5 sec query duration
* RLS roles configured and tested
* Refresh schedule aligned to source
* Documentation: Purpose, owner, SLA, refresh cadence
* Stakeholder review and sign-off
* Published to app; access permissions granted
