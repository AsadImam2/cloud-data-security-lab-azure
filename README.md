# Cloud Data Security & Resilience Lab

A Python-based cybersecurity lab demonstrating core cloud data security concepts, including data classification, encryption, key management, backup security, data loss prevention, regional compliance, audit logging, and recovery validation.

This project was developed for hands-on learning and portfolio development in cloud security.

## Project Objectives

- Understand how sensitive data can be classified and protected.
- Implement authenticated encryption using AES-256-GCM.
- Demonstrate encryption key management and key rotation.
- Create backups while excluding raw encryption keys by default.
- Detect potentially sensitive information using DLP scanning.
- Evaluate data-region policies through compliance checks.
- Record security-relevant events using audit logging.
- Validate encrypted data recovery and rejection of incorrect keys.

## Technologies Used

- **Language:** Python
- **Encryption:** AES-256-GCM
- **Testing:** pytest
- **Cryptography library:** `cryptography`
- **Environment:** Local Python virtual environment on Windows

## Project Modules

| Module | Purpose |
|---|---|
| `inventory.py` | Data inventory and classification |
| `encryption.py` | Encrypt and decrypt data using AES-256-GCM |
| `key_manager.py` | Manage encryption keys and demonstrate key rotation |
| `backup_manager.py` | Create backups and exclude raw keys by default |
| `dlp_scanner.py` | Scan data for potentially sensitive information |
| `region_compliance.py` | Check data-region policy compliance |
| `audit_logger.py` | Record security-related events |

The test suite also validates backup creation, key exclusion, recovery behavior, and incorrect-key rejection.

## Security Features

## Azure Cloud Implementation

In addition to the local Python simulation, selected data-security controls were configured and tested in Microsoft Azure Storage using a student subscription.

### Azure Resources

- **Storage account:** `cloudsecuritylab`
- **Blob container:** `security-lab-data`
- **Sample blob:** `confidential-record.txt`
- **Inventory report container:** `blob-inventory-reports`

### Controls Configured and Verified

| Control | Implementation / Evidence |
|---|---|
| Encryption at rest | Blob properties showed `Server encrypted: true`. |
| Anonymous access protection | Anonymous blob access was disabled at the storage-account level. |
| Public access verification | A direct unauthenticated browser request returned `PublicAccessNotPermitted`. |
| Network restrictions | Public network access was set to selected networks, with two IPv4 entries configured. |
| Trusted services exception | The trusted Microsoft services network exception was enabled. |
| Blob versioning and recovery | An earlier blob version was successfully made the current version. |
| Soft delete | Blob and container soft delete were configured with a 7-day retention period. |
| Change feed | Blob change feed was enabled. |
| Lifecycle management | A lifecycle rule was saved to move the specified base blob to the Cool tier when it meets the configured age condition of more than 30 days. |
| Blob inventory | A daily CSV inventory rule was saved for `security-lab-data/confidential-record.txt`, with all available inventory fields selected. |

### Verification Notes

The unauthenticated browser test confirmed that public blob access was rejected. This demonstrates the configured public-access restriction; it does not prove that every possible unauthorized access path is blocked.

The inventory rule was saved successfully, but the inventory report had not appeared in the destination container during this lab session. Report generation and output validation remain pending.

The lifecycle rule was configured, but its actual tier transition was not observed. Azure may take time to apply lifecycle policies.

### Scope and Limitations

This was a practical configuration exercise in an Azure Storage environment, not a production security audit. Network restrictions, trusted-service exceptions, encryption settings, and access permissions should be reviewed against the intended security requirements.

No claim is made that Azure automatically classified the blob's content as Confidential. The inventory rule collects blob metadata; content classification requires a separate classification capability or process.

### 1. Data Classification

Organizes and classifies data according to its sensitivity, helping establish appropriate protection requirements.

### 2. Encryption at Rest

Uses AES-256-GCM authenticated encryption. The implementation generates a fresh 12-byte nonce for each encryption operation and validates ciphertext integrity during decryption.

### 3. Key Management and Rotation

Maintains key identifiers and metadata through a key manifest. Encrypted records identify the key ID required for decryption, allowing the application to select the corresponding key.

### 4. Secure Backup Defaults

The backup process includes encrypted data and the key manifest but excludes raw encryption key files by default.

Including raw key material requires explicit opt-in. Backups containing keys require stronger protection because anyone who obtains the relevant key may be able to decrypt the associated data.

**Important:** Excluding keys from a backup protects against accidental key exposure, but recovery still depends on separately preserving the required keys.

### 5. Data Loss Prevention (DLP)

Demonstrates scanning for potentially sensitive data patterns. Detection results depend on the rules and patterns implemented in the scanner.

### 6. Data-Region Compliance

Demonstrates checking data-location information against configured region policies. This is a policy simulation, not a complete regulatory compliance assessment.

### 7. Audit Logging

Records security-relevant application events to support monitoring, troubleshooting, and investigation.

### 8. Backup Recovery Validation

Tests that backed-up encrypted files can be decrypted using the corresponding keys and that decryption with an incorrect key is rejected.

## Project Structure

The project follows a source-and-tests layout:

```text
cloud-data-security-lab/
├── src/
│   ├── inventory.py
│   ├── encryption.py
│   ├── key_manager.py
│   ├── backup_manager.py
│   ├── dlp_scanner.py
│   ├── region_compliance.py
│   └── audit_logger.py
├── tests/
│   ├── test_backup_manager.py
│   └── test_key_recovery.py
├── data/
│   ├── encrypted/
│   └── backups/
├── keys/
├── .venv/
└── README.md
```

*Note: This is a high-level structure. Other test files and project files may also exist in the actual repository.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd cloud-data-security-lab
```

Replace the placeholder with your actual repository URL after publishing the project.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use a process-scoped execution policy adjustment, subject to your system's security policies.

### 3. Install dependencies

```bash
python -m pip install cryptography pytest
```

### 4. Run the tests

```bash
python -m pytest -q
```

## Test Results

The complete test suite passed during development.

```text
27 passed in 0.44s
```

The tests cover implemented security behaviors, including backup handling and encryption-key recovery.

## Security Considerations and Limitations

This project is an educational local simulation, not a production-ready cloud security platform.

- Encryption keys are managed locally rather than through a cloud KMS or dedicated secrets vault.
- Recovery tests use keys stored separately from the encrypted backup within the project environment; this is not a full disaster-recovery exercise.
- Backup files and manifests require appropriate access controls and secure storage.
- DLP scanning can produce false positives or miss sensitive data that does not match configured detection patterns.
- Region checks demonstrate policy logic but do not independently prove legal or regulatory compliance.
- Audit logs need additional protection against tampering and unauthorized access in a production environment.
- Selected cloud-provider security controls have been configured and tested in Microsoft Azure Storage. The local Python simulation and Azure implementation are separate parts of this educational project. Some Azure controls are configured but their resulting reports or lifecycle actions have not yet been fully verified.

Never commit real credentials, raw encryption keys, sensitive backups, or environment files containing secrets.

## Future Improvements

- Integrate a cloud KMS or secrets-management service.
- Add automated backup restoration and integrity checks.
- Introduce role-based access control for sensitive operations.
- Improve DLP detection and reporting.
- Add structured security-event logging and monitoring.
- Extend testing for key rotation, backup failures, and recovery scenarios.
- Deploy selected controls in a cloud environment for practical validation.

## Disclaimer

This project is intended for educational purposes, authorized security testing, and cybersecurity portfolio development. It is not a substitute for a professionally reviewed production security architecture.

## Author

Cybersecurity and Cloud Security Learner

**Focus areas:** Data protection, encryption, identity and access management, cloud security, and security testing.