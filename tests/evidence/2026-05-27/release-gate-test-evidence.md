# Release Gate Test Evidence: ASTREB Local Governed MVP v0.3

Date: 2026-05-27
Scope: Local security-baseline verification after strict TESTBOX runtime authorization
Branch: `release/local-governed-mvp-v0.3`
Branch base commit before controlled snapshot: `b8a62934fe4564484793cadf0382696c15c4fef2`

## Test Execution

Command executed locally:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
backend\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests -q
```

Observed result:

```text
........................................................................ [ 70%]
..............................                                           [100%]
102 passed in 12.71s
```

## Verified Controls

- All TESTBOX runtime API endpoints require shared admin-token authorization.
- ASTI administrative operations reject requests without valid authorization.
- External Telegram execution is blocked unless separately enabled.
- META-QMS proposal/decision workflow remains human-governed.
- Clipboard bridge is protected in addition to its local-host restriction.
- Runtime tests use temporary isolated storage rather than raw project stores.

## Environment Summary

| Item | Evidence |
| --- | --- |
| Execution context | Local Windows workspace; no production deployment involved. |
| Dependencies declared | `fastapi==0.115.6`, `uvicorn==0.34.0`, `pytest==8.3.4`, `httpx==0.28.1`. |
| Bytecode/cache control | `PYTHONDONTWRITEBYTECODE=1`, pytest cache plugin disabled. |
| Python version capture | Not recorded: a direct virtualenv version query returned a local launcher resolution error after the successful test run. |
| Raw stores | Excluded from Git and not included in this evidence artifact. |
| Secrets | No secret values recorded in evidence. |

## SHA-256 Evidence Hashes

```text
b1b61eeb740d74022166061ae587fa7e9ec589ccb2fe908767db1378d2b51fdd  backend/runtime_auth.py
7e2f96e780f5f4e1e7e185eb12be2d132aa8de70dc4e72618bcd6a891a8b9009  backend/testbox_runtime/api.py
e9c7780eb8b41bd3a5119407f8a178a4eebf39af8713bec6fe16f9b3615266df  backend/asti/service.py
4d944854eb97c93fc50596622b5229d8129d09cfb5fb4103f6af2476cd8fbf90  .github/workflows/ci.yml
e2cbd1f9efc30c8044bc1dcd64e6cd86752d7ea2d1a10b02648407ad3f425f4a  .gitignore
f78194cad26f1f7e263afd21d5150bf098c0d27c14ef4ded5bd091f085b99ecc  .env.example
5de5df9d5b6a4aa5398a9ca6e925073f9d0c2fbc523d6e886ad5080e9658716c  docs/release/release-gate-v0.3.md
34f56313ff14173d66842575a0fa2a77d281e68ee7047e01a7f0f554c9f3f39a  docs/release/system-boundaries.md
2bb54e44be28b6730fcca92bcad340b13020f9f37b70ae7e71eb66e688914176  docs/release/production-scope.md
80285a48adc300260a0aed4242996a113a21e94eb918224622a510d6774982cb  docs/release/security-open-risks.md
42b2944c7b8cb9a4ea4b80df652701ee21608ab31569f47ca93db53bee6131e0  docs/release/deployment-checklist.md
37deeed47112bf30a910add9032eb788374f04cf9bb68659845fdf8331932abb  docs/release/production-readiness-report-v0.3-2026-05-27.md
0a6debfb4fdb1cc435d61cfd5e2ff8cc0ceeddf41fc3d25636d0e6b339640089  tests/test_testbox_runtime.py
bbbc01abb51ed1af5e499cc29b5d8067c9a1ba66bf25deedcef838dbf75d7d07  tests/test_asti_telegram_approval.py
18749b7bafa7e1abcdb5a20ffda4dcab469bbcf640062c58f6fbb5dc98522bc6  tests/test_meta_qms_runtime.py
```

Hashes above were calculated after implementation and release-document scope
review, before this evidence document itself is committed. A commit SHA, when
created, becomes the authoritative immutable snapshot identifier.

## Public Preview Screenshots

Captured through a local browser session at a mobile viewport (`390 x 1100`).
These demonstrate visible local UI rendering only.

| Evidence File | Surface | SHA-256 |
| --- | --- | --- |
| `jazekker-home-mobile.png` | `/jazekker` | `7be1ec815003c356211a3dac78441a3d80bc9d8884f8a848abcb1eaf9597aaee` |
| `jazekker-testbox-mobile.png` | `/jazekker/testbox` | `4a18e495596c7822a621c6f7838225dcede4776765b2cef0bea84395223b6715` |

## Evidence Boundary

This report confirms local test execution only. It does not prove CI execution
on GitHub, deployment, operational security of a hosted environment or
authorization of real external execution.
