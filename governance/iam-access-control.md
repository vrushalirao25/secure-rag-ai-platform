# IAM Access Control — Secure RAG AI Platform

## 1. Overview

This document defines access control standards for the Secure RAG AI Platform using AWS Identity and Access Management (IAM).

The objective is to ensure:

* Secure access to data and models
* Controlled interaction between system components
* Enforcement of least privilege principles
* Clear separation of responsibilities

---

## 2. Access Control Principles

The platform follows these core principles:

* **Least Privilege**
  Each component is granted only the permissions it requires

* **Role-Based Access**
  Access is managed through IAM roles, not individual users

* **Environment Isolation**
  Separate roles and permissions for DEV, PREPROD, and PROD

* **No Hardcoded Credentials**
  All access must be managed via IAM roles or secure mechanisms

---

## 3. Key IAM Roles

### 3.1 Application Role (Lambda / API Layer)

Used by:

* AWS Lambda (or API layer)

Permissions:

* `bedrock:InvokeModel` → Invoke LLM and embedding models
* `s3:GetObject` → Read documents from S3
* `logs:CreateLogGroup`, `logs:PutLogEvents` → Logging to CloudWatch

Restrictions:

* Limited to specific model IDs
* Restricted to specific S3 buckets

---

### 3.2 Data Access Role

Used by:

* Retrieval layer components

Permissions:

* `s3:GetObject` → Access knowledge base documents
* (Production) OpenSearch access for vector queries

Restrictions:

* Read-only access
* No write permissions

---

### 3.3 Monitoring Role

Used by:

* Observability systems

Permissions:

* CloudWatch read access
* Metrics and logs access

---

### 3.4 Admin Role

Used by:

* Platform administrators

Permissions:

* Manage IAM roles
* Configure infrastructure
* Deploy platform components

Restrictions:

* Limited to trusted users only
* Not used by application runtime

---

## 4. Environment-Based Access Control

Each environment must have separate IAM roles:

| Environment | Access Level                              |
| ----------- | ----------------------------------------- |
| DEV         | Broad access for development (controlled) |
| PREPROD     | Restricted access for testing             |
| PROD        | Strict, minimal access                    |

Important:

* No cross-environment access
* Production roles must not be used in lower environments

---

## 5. Service-to-Service Access

Access between components must be controlled:

* Lambda → Bedrock
* Lambda → S3
* Lambda → CloudWatch

This access is granted via:

* IAM role attached to the service
* No direct credential sharing

---

## 6. Security Controls

* All access must be authenticated via IAM
* Policies must be reviewed regularly
* Sensitive actions must be logged

Additional considerations:

* Restrict model access to approved models only
* Prevent public access to S3 buckets
* Enforce encryption for data access

---

## 7. Example Policy (Simplified)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1",
        "arn:aws:s3:::rag-prod-bucket/*"
      ]
    }
  ]
}
```

> Production policies must always specify exact resource ARNs.
> Wildcard (*) resources are not permitted in PROD environments.


Note:
In production, resources should be scoped to specific ARNs.

---

## 8. Common Risks & Mitigation

| Risk                      | Mitigation                            |
| ------------------------- | ------------------------------------- |
| Over-permissioned roles   | Enforce least privilege               |
| Credential leakage        | Use IAM roles instead of keys         |
| Cross-environment access  | Separate roles per environment        |
| Unauthorized model access | Restrict model invocation permissions |

---

## 9. Summary

IAM access control ensures that the RAG platform operates securely and reliably.

The focus is on:

* Least privilege access
* Role-based control
* Secure interaction between components

This approach enables safe scaling of AI systems in production environments.
