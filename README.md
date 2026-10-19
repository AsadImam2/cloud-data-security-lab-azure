# Cloud Data Security & Resilience Lab

A hands-on cybersecurity project demonstrating cloud data security concepts through a local Python simulation and selected Microsoft Azure Storage security controls.

The project focuses on data classification, encryption, key management, recovery, storage access restrictions, versioning, lifecycle management, and audit-related capabilities.

## Project Overview

Cloud environments store data with different sensitivity levels and security requirements. This project explores how to protect that data using local security mechanisms and real cloud-provider controls.

The lab has two separate components:

- **Local Python Lab:** Simulates data security and resilience concepts using Python modules and automated tests.
- **Azure Cloud Implementation:** Applies selected storage security controls in Microsoft Azure and verifies their observable behavior.

The local simulation and Azure implementation are separate parts of the same educational project. A successful local test does not automatically prove that the equivalent Azure control is configured or working.

## Project Objectives

- Classify data according to sensitivity.
- Demonstrate authenticated encryption and tamper detection.
- Explore encryption key management and rotation.
- Apply secure defaults to backup-related workflows.
- Demonstrate data loss prevention (DLP) concepts.
- Explore data-region and compliance considerations.
- Maintain security-related audit records.
- Validate backup and recovery behavior.
- Configure and test selected Azure Storage security controls.
- Document verified results, limitations, and remaining validation work.

## Technologies Used

- Python
- AES-256-GCM authenticated encryption
- `cryptography`
- `pytest`
- Microsoft Azure Storage
- Azure Blob Storage
- Git and GitHub
- Windows PowerShell

## Architecture and Scope

| Component | Purpose |
|---|---|
| Local Python simulation | Demonstrates data security concepts in a controlled environment |
| Local test suite | Checks expected behavior and selected failure cases |
| Azure Storage account | Provides a real cloud environment for storage security practice |
| Azure Blob containers | Separate sample data from inventory-report storage |
| GitHub repository | Documents implementation, tests, and learning outcomes |

## Local Python Lab Features

### 1. Data Classification and Inventory

- Maintains a sample data inventory.
- Demonstrates four sensitivity levels: Public, Internal, Confidential, and Highly Confidential.
- Validates inventory records and required fields.
- Generates a local inventory report.

**Validation:** The local inventory test suite checks valid records, invalid sensitivity values, missing fields, and negative retention values.

### 2. Encryption at Rest

- Uses AES-256-GCM for authenticated encryption.
- Uses a fresh 12-byte nonce for encryption operations.
- Demonstrates encryption and decryption of sample data.
- Checks that modified ciphertext is rejected.
- Tests decryption with an incorrect key.

### 3. Key Management and Rotation

- Demonstrates local encryption key management.
- Maintains a key manifest for the lab.
- Demonstrates moving to a new key version.
- Excludes raw key material and the local key manifest from Git tracking.

**Limitation:** This is a local educational implementation, not a production key-management service or a replacement for a cloud KMS/HSM.

### 4. Secure Backup Defaults

- Demonstrates safer backup-related handling of data.
- Excludes sensitive key material from the intended repository and backup workflows.

### 5. Data Loss Prevention (DLP)

- Demonstrates selected DLP-related concepts in the local lab.
- Supports learning about sensitive-data exposure and reducing data leakage risks.

### 6. Data-Region and Compliance Considerations

- Includes data-region information in the local inventory.
- Demonstrates how data location and retention requirements can be documented.

**Limitation:** Recording a region in a local inventory does not establish legal or regulatory compliance.

### 7. Audit Logging

- Includes audit-related logging concepts for security operations.
- Supports investigation and verification of selected lab activities.

### 8. Backup and Recovery Validation

- Includes recovery-related functionality and tests.
- Demonstrates why recovery must be validated rather than assumed to work.

## Azure Cloud Implementation

Selected controls were configured and tested in Microsoft Azure Storage using the following resources.

### Azure Resources

| Resource | Name / Configuration |
|---|---|
| Storage account | `cloudsecuritylab` |
| Sample data container | `security-lab-data` |
| Sample blob | `confidential-record.txt` |
| Inventory report container | `blob-inventory-reports` |

### Implemented Controls and Observed Results

| Security control | Configuration or observed result |
|---|---|
| Encryption at rest | Azure blob properties showed `Server encrypted: true` |
| Anonymous blob access | Disabled at the storage-account level |
| Anonymous access verification | Unauthenticated request returned `PublicAccessNotPermitted` |
| Secure transfer | Required |
| Minimum TLS version | TLS 1.2 |
| Storage account key access | Disabled |
| Encryption key management | Microsoft-managed encryption keys |
| Infrastructure encryption | Enabled |
| Blob versioning | Enabled; an earlier version was restored as the current version |
| Blob soft delete | Enabled with a 7-day retention period |
| Container soft delete | Enabled with a 7-day retention period |
| Blob change feed | Enabled; the change-feed container and log files were observed |
| Public network access | Enabled from selected networks |
| Network access rules | Two IPv4 entries configured; no virtual-network rules configured |
| Trusted Microsoft services | Exception enabled |
| Lifecycle management | Rule saved to move the specified base blob to Cool after more than 30 days |
| Blob inventory | Daily CSV inventory rule saved for the specified blob prefix |

### Azure Verification Notes

**Anonymous access restriction**

An unauthenticated request to the blob returned the following error:

`PublicAccessNotPermitted`

This verifies that the tested anonymous request was rejected by the storage account. It does not independently prove that every access path, identity, credential, or network rule has been tested.

**Blob versioning and recovery**

Blob versioning was enabled. An earlier version of `confidential-record.txt` was made current, and the restored blob size was observed as 133 bytes.

This demonstrates a successful version-restoration action in the lab. It is not a substitute for testing a complete disaster-recovery process.

**Blob soft delete and container soft delete**

Both features were configured with a seven-day retention period. Their settings were verified in Azure. A separate deletion-and-recovery test should be performed before claiming that the complete recovery workflow has been tested.

**Blob change feed**

The `$blobchangefeed` container and associated log files were observed. The files were not decoded and analyzed, so detailed event contents have not been verified.

**Network restrictions**

The storage account was configured for selected-network access with two IPv4 entries and the trusted Microsoft services exception enabled. The configuration was observed in the portal, but the actual IP addresses and access behavior from each permitted and unpermitted network have not been comprehensively tested.

**Lifecycle management**

The `lab-confidential-data-tiering` rule was saved for the specified base blob, with a condition to move it to the Cool tier after more than 30 days.

The rule's configuration was saved, but an actual lifecycle transition has not yet been observed. Saving a rule alone does not prove that a blob has transitioned tiers.

**Blob inventory**

The `confidential-data-inventory` rule was saved with daily CSV output, all available fields selected, and the prefix:

`security-lab-data/confidential-record.txt`

The rule includes a 30-day creation-time filter. The inventory report has not yet been observed in `blob-inventory-reports`, so successful report generation and its contents remain unverified.

**Important distinction:** Azure Blob Inventory reports blob metadata. It does not automatically inspect the contents of a blob and classify them as Confidential or Highly Confidential. The local Python classification module and Azure inventory feature serve different purposes.

## Project Structure

The project contains separate source-code, test, sample-data, key, report, and log areas. The following is a high-level view; the exact module and test filenames should match the files present in the repository.

```text
cloud-data-security-lab/
├── data/
│   └── sample/
├── keys/
├── logs/
├── reports/
├── src/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

Generated reports, local sample data, encryption keys, encrypted files, virtual-environment files, and other excluded artifacts may exist locally without being tracked by Git.

The repository's `.gitignore` excludes the local virtual environment and Python caches, sensitive key files, local encrypted data, generated JSON reports, and local data directories.

## Getting Started

### Prerequisites

- Python installed
- Git installed
- PowerShell on Windows, or an equivalent terminal
- A Microsoft Azure account only if you want to reproduce the cloud implementation

### 1. Clone the Repository

```powershell
git clone https://github.com/AsadImam2/cloud-data-security-lab.git
cd cloud-data-security-lab
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of the execution policy, you can temporarily allow scripts for the current PowerShell process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again.

### 4. Install Dependencies

If `requirements.txt` is present and contains the project's dependencies:

```powershell
python -m pip install -r requirements.txt
```

### 5. Run the Tests

```powershell
python -m pytest
```

The test suite has previously completed successfully with **27 passing tests**.

The execution time varies between runs, and the result may change as the project evolves. Run the tests locally to verify the current repository state.

## Security Considerations and Limitations

- This project is an educational lab, not a production-ready cloud security platform.
- Local encryption keys and key manifests must never be committed to Git.
- Local key management does not provide all the protections of a managed KMS or HSM.
- The local Python simulation and Azure configuration must be validated independently.
- Encryption at rest does not prevent every form of unauthorized access or data exposure.
- Network restrictions, identity permissions, and storage access controls require separate testing.
- A saved lifecycle rule does not prove that a lifecycle transition has occurred.
- A saved inventory rule does not prove that a report has been generated successfully.
- Data classification in the local inventory does not automatically classify Azure blob contents.
- Soft delete and versioning support recovery, but do not replace a complete backup and disaster-recovery strategy.
- Configuring selected storage controls does not establish full regulatory compliance.
- Azure resource names and settings documented here describe this lab and may need to be adjusted when reproducing it in another subscription.

## Future Improvements

- Verify Azure Blob Inventory report generation and inspect the resulting CSV.
- Validate lifecycle tier transitions when the configured conditions are met.
- Test storage access from allowed and denied network locations.
- Perform a controlled soft-delete and recovery test.
- Decode and inspect selected change-feed events.
- Expand Azure identity-based access-control testing.
- Explore managed key services and key-rotation workflows.
- Add further automated tests and improve recovery validation.
- Add sanitized screenshots and test evidence to the repository.
- Improve monitoring and alerting for relevant storage-security events.

## Author

Cybersecurity and Cloud Security Learner

This project is part of an ongoing hands-on learning journey in cloud security, data protection, and security engineering.
