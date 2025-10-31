# PERF-004 - Database Load Profiling and Optimization

## Metadata
- **Category**: performance
- **Priority**: low
- **Complexity**: moderate
- **Duration**: 30-60 minutes
- **Environment**: local/staging
- **Dependencies**: crawlab-master, crawlab-worker(s), mongodb
- **Target Release**: 0.7.1

## Scenario
This test validates MongoDB query patterns and resource usage to identify optimization opportunities, specifically addressing issue #1597 (30% MongoDB load with idle workers). The test profiles database activity during idle and active periods, identifies inefficient query patterns, analyzes connection pool usage, and validates index effectiveness.

While not a blocker for 0.7.0, this test provides valuable insights for optimizing database performance and reducing infrastructure costs. The test can run alongside normal operations without disrupting system functionality.

## Prerequisites
- Crawlab master node running with MongoDB
- At least 1 worker node (idle state)
- MongoDB profiling enabled or accessible
- Database monitoring tools (optional: mongo-express, Compass)
- Python environment with pymongo installed
- Sufficient permissions to query MongoDB system collections

## Test Steps

### Step 1: Baseline Idle Worker Monitoring
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step baseline`
**Expected**: Capture baseline metrics with idle workers
**Validation**: 
- System running with no active tasks
- All workers in idle state (no task execution)
- MongoDB connection count recorded
- Query frequency measured (queries per second)
- Sample 5-minute idle period to establish baseline
- Record:
  - Active connections: Expected < 10 per worker
  - Queries per second: Expected < 5 for idle system
  - Connection pool usage: Expected < 20%
  - Top 10 most frequent query patterns

**Baseline Thresholds** (idle system):
```
Queries per second: < 5
Active connections: < 10
Connection pool usage: < 20%
Slow queries (>100ms): 0
```

### Step 2: Query Pattern Analysis
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-queries`
**Expected**: Identify all query patterns and frequencies
**Validation**: 
- MongoDB profiler data collected (or parse logs)
- Queries grouped by collection and operation type
- Top 10 most frequent queries identified
- Query execution times analyzed
- Check for:
  - ✅ Queries using proper indexes
  - ⚠️ Collection scans (table scans)
  - ⚠️ Queries without indexes
  - ⚠️ Redundant/duplicate queries
  - ⚠️ Polling queries that could use change streams

**Query Pattern Report**:
```
Top Queries (by frequency):
1. nodes collection - find({}) - 120 queries/min
2. tasks collection - find({status: "pending"}) - 60 queries/min
3. spiders collection - find({}) - 30 queries/min
4. stats collection - aggregate(...) - 20 queries/min
5. ...

Problematic Patterns:
- ⚠️ Frequent polling of nodes collection (could use change streams)
- ⚠️ Repeated full collection scans on tasks
- ⚠️ No indexes on commonly queried fields
```

### Step 3: Connection Pool Analysis
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-connections`
**Expected**: Analyze connection pool usage and efficiency
**Validation**: 
- Total connections vs pool limit
- Active vs idle connections ratio
- Connection churn rate (new connections per minute)
- Long-lived vs short-lived connections
- Connection leaks detection
- Validate:
  - Pool size appropriate for workload
  - Connections properly released
  - No connection exhaustion
  - Idle timeout settings optimal

**Connection Pool Metrics**:
```
Pool Configuration:
  - Max pool size: 100
  - Min pool size: 10
  - Current active: 8
  - Current idle: 12
  - Total: 20 (20% utilization)

Connection Activity:
  - New connections/min: 2
  - Closed connections/min: 2
  - Avg connection lifetime: 15 minutes
  - Leaked connections: 0
  
Health: ✅ HEALTHY (low utilization, stable)
```

### Step 4: Index Effectiveness Analysis
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-indexes`
**Expected**: Evaluate index usage and identify missing indexes
**Validation**: 
- Query execution plans analyzed (explain plans)
- Index hit ratio calculated
- Missing index recommendations generated
- Unused indexes identified (candidates for removal)
- Index size vs collection size
- Check for:
  - Queries doing collection scans
  - Composite indexes needed
  - Covered queries (index-only)
  - Index cardinality issues

**Index Analysis Report**:
```
Collection: tasks
  Existing Indexes:
    - _id (auto)
    - status (single field) - Hit rate: 85%
    - spider_id (single field) - Hit rate: 45%
  
  Recommendations:
    - ✅ Add compound index: {status: 1, created_ts: -1}
      Reason: Frequent query pattern for pending tasks sorted by time
      Impact: ~60% of queries would benefit
    
    - ⚠️ Consider index: {node_id: 1, status: 1}
      Reason: Worker queries for node-specific tasks
      Impact: ~30% of queries would benefit
    
    - ❌ Remove index: {deprecated_field: 1}
      Reason: Never used in queries, wastes space
      Impact: -50MB disk space

Collection: nodes
  Issue: Full collection scans detected
  Recommendation: Add index on {active: 1, enabled: 1}
```

### Step 5: Slow Query Identification
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step slow-queries`
**Expected**: Identify queries taking > 100ms
**Validation**: 
- MongoDB slow query log analyzed
- Queries > 100ms threshold identified
- Execution plan for slow queries examined
- Root cause analysis:
  - Missing indexes
  - Large result sets
  - Complex aggregations
  - Inefficient query structure
- Optimization recommendations provided

**Slow Query Report**:
```
Slow Queries (>100ms):
1. Query: db.tasks.find({}).sort({created_ts: -1}).limit(100)
   Time: 350ms
   Issue: No index on created_ts for sorting
   Fix: Add index {created_ts: -1}
   
2. Query: db.nodes.aggregate([{$lookup: ...}])
   Time: 280ms
   Issue: Complex aggregation with multiple joins
   Fix: Consider denormalization or caching
   
3. Query: db.stats.find({timestamp: {$gte: ...}})
   Time: 150ms
   Issue: Large collection scan
   Fix: Add index on timestamp, consider TTL index
```

### Step 6: Active Load Monitoring
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step active-load`
**Expected**: Compare metrics under active task execution
**Validation**: 
- Start moderate task load (50-100 concurrent tasks)
- Monitor database metrics during execution
- Compare with baseline idle metrics
- Measure:
  - Query rate increase
  - Connection pool usage
  - Slow query count
  - Lock contention (if any)
  - CPU and memory impact on MongoDB

**Active Load Thresholds**:
```
Queries per second: < 50
Active connections: < 30
Connection pool usage: < 50%
Slow queries (>100ms): < 5/min
```

### Step 7: Generate Optimization Report
**Method**: script
**Command**: `uv run python runners/performance/PERF_004_database_load_profiling.py --step generate-report`
**Expected**: Comprehensive optimization recommendations
**Validation**: 
- All analysis data compiled
- Priority recommendations generated:
  - **HIGH**: Critical performance impacts
  - **MEDIUM**: Moderate improvements
  - **LOW**: Nice-to-have optimizations
- Estimated impact quantified
- Implementation steps provided
- Before/after metrics projected

**Report Sections**:
1. Executive Summary
2. Current State Analysis
3. Identified Issues (by severity)
4. Index Recommendations
5. Query Optimization Suggestions
6. Connection Pool Tuning
7. Architectural Recommendations
8. Implementation Roadmap
9. Expected Performance Gains

## Success Criteria

### Baseline Metrics
- [ ] Idle query rate < 5 queries/second
- [ ] Connection pool usage < 20% when idle
- [ ] No slow queries detected during idle
- [ ] All connections properly released

### Analysis Quality
- [ ] Query patterns categorized and documented
- [ ] Top 10 most frequent queries identified
- [ ] Index hit ratio calculated (target: >90%)
- [ ] Missing indexes identified with justification
- [ ] Slow queries (>100ms) cataloged with fixes
- [ ] Connection pool efficiency analyzed

### Optimization Recommendations
- [ ] At least 3 actionable recommendations
- [ ] Each recommendation has:
  - Clear problem statement
  - Root cause analysis
  - Specific implementation steps
  - Estimated performance impact
- [ ] Recommendations prioritized (HIGH/MEDIUM/LOW)

### Report Completeness
- [ ] All metrics collected successfully
- [ ] Visualizations generated (charts, graphs)
- [ ] Before/after projections included
- [ ] Implementation roadmap provided
- [ ] Report exported in multiple formats (JSON, HTML, PDF)

## Failure Scenarios

### Scenario: Cannot Enable MongoDB Profiling
- **Symptoms**: Profiler not accessible, insufficient permissions
- **Action**: 
  1. Use alternative: parse MongoDB logs
  2. Query currentOp() for active queries
  3. Use db.serverStatus() for metrics
  4. Document limitation in report
- **Recovery**: Proceed with available metrics

### Scenario: High Database Load During Test
- **Symptoms**: Background tasks causing noise in metrics
- **Action**:
  1. Wait for load to subside
  2. Or run test during off-peak hours
  3. Document anomalies in report
  4. Re-run baseline if needed
- **Recovery**: Reschedule test or filter outliers

### Scenario: Missing Index Statistics
- **Symptoms**: MongoDB version doesn't support $indexStats
- **Action**:
  1. Use explain() for individual queries
  2. Manually track index usage
  3. Query system.indexes collection
- **Recovery**: Use alternative analysis methods

### Scenario: Connection Pool Full
- **Symptoms**: "Too many connections" errors during test
- **Action**:
  1. This itself is a finding - pool too small
  2. Increase pool size temporarily for test
  3. Document as critical issue
  4. Recommend pool size increase
- **Recovery**: Immediate finding for report

## Execution

### Automated (Recommended)
```bash
# Full analysis (all steps)
cd crawlab-test
uv run python runners/performance/PERF_004_database_load_profiling.py --full

# Individual steps
uv run python runners/performance/PERF_004_database_load_profiling.py --step baseline
uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-queries
uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-connections
uv run python runners/performance/PERF_004_database_load_profiling.py --step analyze-indexes
uv run python runners/performance/PERF_004_database_load_profiling.py --step slow-queries
uv run python runners/performance/PERF_004_database_load_profiling.py --step active-load
uv run python runners/performance/PERF_004_database_load_profiling.py --step generate-report

# Quick profiling (baseline + report only)
uv run python runners/performance/PERF_004_database_load_profiling.py --quick

# Via test CLI
./cli.py --spec PERF-004
```

### Manual Monitoring
```bash
# Enable MongoDB profiling (level 2 = all operations)
mongo admin --eval "db.setProfilingLevel(2)"

# Monitor current operations
watch -n 5 'mongo admin --eval "db.currentOp()" | jq'

# Check connection count
mongo admin --eval "db.serverStatus().connections"

# View slow queries
mongo local --eval "db.system.profile.find({millis: {\$gt: 100}}).sort({ts: -1}).limit(10).pretty()"

# Monitor query patterns
mongostat --host localhost:27017 -n 100 5

# Connection pool stats
mongo admin --eval "db.serverStatus().connections" | jq
```

## Cleanup
```bash
# Disable profiling (reduce overhead)
mongo admin --eval "db.setProfilingLevel(0)"

# Clear profile collection (optional)
mongo local --eval "db.system.profile.drop()"

# Archive analysis results
uv run python runners/performance/PERF_004_database_load_profiling.py --archive
```

## Expected Test Outputs

### Metrics Dashboard (Example)
```
🔬 Crawlab MongoDB Load Profiling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Test Status: COMPLETE (45 minutes)

📈 Database Metrics (5-min baseline):
  Queries/sec:        4.2 ✅ (target: <5)
  Active connections: 8 ✅ (target: <10)
  Pool usage:        16% ✅ (target: <20%)
  Slow queries:       0 ✅ (target: 0)

🔍 Query Analysis:
  Total unique patterns: 47
  Most frequent: nodes.find({}) - 120 queries/min ⚠️
  Collection scans: 12 patterns identified ⚠️
  Index usage: 78% (target: >90%) ⚠️

💾 Connection Pool:
  Configured max: 100
  Current usage: 16/100 (16%)
  Avg lifetime: 12 minutes
  Churn rate: 2 new/min
  Status: ✅ HEALTHY

📑 Top Recommendations:
  1. HIGH: Add compound index on tasks.{status,created_ts}
     Impact: 60% of queries, -40% query time
  
  2. MEDIUM: Use change streams instead of polling nodes
     Impact: -80% query volume, -30% CPU
  
  3. MEDIUM: Add index on stats.timestamp with TTL
     Impact: -50% slow queries

📊 Report: results/PERF-004_20251031_120000/report.html
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### JSON Report (Excerpt)
```json
{
  "test_id": "PERF-004",
  "test_type": "database-load-profiling",
  "duration_minutes": 45,
  "timestamp": "2025-10-31T12:00:00Z",
  "test_result": "PASS",
  
  "baseline_metrics": {
    "queries_per_second": 4.2,
    "active_connections": 8,
    "pool_utilization_percent": 16,
    "slow_queries_count": 0
  },
  
  "query_analysis": {
    "total_patterns": 47,
    "top_queries": [
      {
        "pattern": "nodes.find({})",
        "frequency_per_min": 120,
        "avg_duration_ms": 15,
        "uses_index": false,
        "recommendation": "Add index on commonly filtered fields"
      }
    ],
    "collection_scans": 12,
    "index_hit_rate_percent": 78
  },
  
  "recommendations": [
    {
      "priority": "HIGH",
      "category": "indexing",
      "issue": "No index on tasks sort field",
      "recommendation": "Add compound index: {status: 1, created_ts: -1}",
      "estimated_impact": "60% of queries affected, -40% query time",
      "implementation": "db.tasks.createIndex({status: 1, created_ts: -1})"
    }
  ]
}
```

## Notes

### Test Philosophy
- **Non-invasive**: Test runs alongside normal operations
- **Observational**: Primarily monitoring, not stress testing
- **Actionable**: Focus on concrete, implementable recommendations
- **Quantified**: All recommendations include estimated impact

### MongoDB Profiling Levels
- **Level 0**: Off (no overhead)
- **Level 1**: Slow queries only (>100ms default)
- **Level 2**: All operations (use during test only, high overhead)

### Analysis Techniques
1. **Query Pattern Analysis**: Group by collection, operation, filter
2. **Index Effectiveness**: Compare queries with/without indexes
3. **Connection Monitoring**: Track pool usage, churn, leaks
4. **Performance Baseline**: Idle vs active load comparison

### Common Optimizations
1. **Indexing**: Add missing indexes, remove unused
2. **Query Rewriting**: Optimize aggregations, use projections
3. **Change Streams**: Replace polling with reactive updates
4. **Connection Pooling**: Right-size pool, tune timeouts
5. **Caching**: Cache frequently accessed, rarely changing data

### Production Considerations
- Run during low-traffic periods
- Enable profiling temporarily only
- Monitor MongoDB resource usage
- Profile collection can grow large (clear periodically)
- Some optimizations require application code changes

## Implementation Status
- **Specification**: ✅ Complete (2025-10-31)
- **Test Runner**: ⏳ Pending (scheduled for 0.7.1)
- **Priority**: LOW - Not blocking 0.7.0 release
- **Target**: 0.7.1 (optimization release)

## History
- **Created**: 2025-10-31, AI Agent
- **Target Release**: 0.7.1
- **Related Issue**: #1597 (30% MongoDB load with idle workers)
