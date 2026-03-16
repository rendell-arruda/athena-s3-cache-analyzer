# athena-s3-cache-analyzer

Analyzes S3 buckets used by Amazon Athena as query result locations (cache).

These buckets are often overlooked in cost reviews — they accumulate query results over time, may lack billing tags, and can generate significant unexpected S3 storage costs.

---

## What it does

- Lists all Athena workgroups and their configured output locations
- Identifies which S3 buckets are being used as query result cache
- Analyzes bucket size and estimated monthly storage cost
- Flags buckets without lifecycle policies

---

## Requirements

- Python 3.11+
- AWS credentials configured (`aws configure` or environment variables)
- IAM permissions:
  - `athena:ListWorkGroups`
  - `athena:GetWorkGroup`
  - `s3:ListBucket`
  - `s3:GetBucketLifecycleConfiguration`
  - `cloudwatch:GetMetricStatistics`

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/athena-s3-cache-analyzer.git
cd athena-s3-cache-analyzer
pip install -r requirements.txt
```

---

## Usage

```bash
# Default (uses current AWS profile and us-east-1)
python scripts/athena_cache_analyzer.py

# With specific profile and region
python scripts/athena_cache_analyzer.py --profile myprofile --region us-east-1

# Export results to CSV
python scripts/athena_cache_analyzer.py --output csv
```

---

## Output example

```
🔍 Collecting Athena workgroups (us-east-1)...
   3 workgroup(s) found.

📦 Analyzing S3 cache buckets...

  → s3://my-athena-results-bucket
     Workgroups : primary, data-team
     Size       : 12.45 GB
     Est. cost  : $0.29 / month
     Lifecycle  : ❌ no lifecycle policy
```

---

## Roadmap

- [ ] CSV export
- [ ] Tag analysis (owner/billing)
- [ ] Multi-region support
- [ ] Estimated cost breakdown by workgroup

---

## Author

Rendell — FinOps Engineer  
Part of a personal AWS FinOps tooling lab.