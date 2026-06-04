# TESTBOX v0.2 Acceptance Cases

## TBX-BUS-ENERGY-001

**Pattern:** Governed business orientation case

**Purpose:** Prevent regression from domain-aware governance routing back to generic chat handling.

### User Input

```text
хочу открыть компанию по производству источников хранения электричества
```

### Expected Runtime Classification

| Field | Expected |
| --- | --- |
| `intent` | `launch_regulated_energy_storage_manufacturing_business` |
| `primary_domain` | Not `general` |
| `domains` | Includes `business_formation`, `battery_manufacturing` |
| `jurisdiction` | `Netherlands (candidate)` |
| `source_required` | `true` |
| `route` | `Legal Retrieval -> Governed Draft -> Human Review` |
| `human_review_reason` | `regulated_energy_storage_manufacturing_requires_specialist_review` |

### Prohibited Behavior

- No fallback to general chat.
- No false `contracts` missing-source warning unless contracts are explicitly requested.
- No internal enum values such as `RiskLevel.HIGH` or `REQUIRES_HUMAN_REVIEW` in the user-facing answer.

### Expected Answer Coverage

The answer must address:

- business formation and possible legal form;
- regulated energy-storage/battery manufacturing;
- EU battery regulation;
- environmental permits for the manufacturing site;
- producer responsibility for batteries placed on the market;
- product placement on the EU market;
- need for specialist review before launch.

### Expected Audit Evidence

The runtime audit must contain:

| Event | Required Payload |
| --- | --- |
| `INTENT_DETECTED` | `intent`, `domains`, `sources_required` |
| `SOURCE_REQUIRED` | `sources_required = true` |
| `ROUTING_SELECTED` | governed retrieval/draft/review route |
| `HUMAN_REVIEW_REQUIRED` | `human_review_reason`, `domains`, `sources_required` |

### Automated Regression Test

```text
tests/test_testbox_runtime.py::test_tbx_bus_energy_001_governed_energy_storage_business_orientation
```

### Expansion Pattern

This scenario is the reference pattern for future regulated business cases:

- medical technology;
- recruitment and employment platforms;
- construction;
- transport;
- food businesses;
- AI/legal services;
- energy and electronics.

## TBX-HOU-SOCIAL-001

**Pattern:** Governed social housing orientation case

### User Input

```text
как мне узнать я имею право на социальное жилье (аренда)
```

### Expected Runtime Classification

| Field | Expected |
| --- | --- |
| `intent` | `check_social_housing_eligibility` |
| `primary_domain` | `social_housing` |
| `jurisdiction` | `Netherlands (candidate)` |
| `source_required` | `true` |
| `route` | `Legal Retrieval -> Governed Draft` |

### Prohibited Behavior

- No fallback to general chat.
- No `business_formation` or `contracts` warning.
- No internal enum values in the user-facing answer.

### Expected Answer Coverage

The answer must:

- explain that the Netherlands route is assumed until municipality/country is confirmed;
- ask for municipality, household composition and approximate annual household income;
- state the applicable 2026 Rijksoverheid social-housing allocation thresholds;
- mention registration with a `woningcorporatie`;
- explain possible `urgentieverklaring` through the municipality.

### Official Source Registry

- `rijksoverheid-social-housing-eligibility`
- `rijksoverheid-social-housing-urgency`

### Automated Regression Test

```text
tests/test_testbox_runtime.py::test_tbx_hou_social_001_routes_social_rental_eligibility_to_official_sources
```

## TBX-EMP-ZEROHOURS-001

**Pattern:** Governed employment contract orientation case

### User Input

```text
мне предлогают заключить нулевой контракт что это значит
```

### Expected Runtime Classification

| Field | Expected |
| --- | --- |
| `intent` | `understand_zero_hours_employment_contract` |
| `primary_domain` | `employment_contract` |
| `jurisdiction` | `Netherlands (candidate)` |
| `source_required` | `true` |

### Expected Answer Coverage

The answer must explain `nulurencontract` as a Dutch on-call employment contract
without fixed hours and cover:

- worker status and basic labour rights;
- call notice rules;
- minimum payment where the 3-hour rule applies;
- fixed-hours offer after 12 months;
- holiday hours and holiday allowance;
- announced regulatory change for zero-hours contracts;
- recommendation to check the contract before signing.

### Official Source Registry

- `rijksoverheid-on-call-contract-types`
- `rijksoverheid-zero-hours-holiday-pay`
- `businessgov-zero-hours-contract`

### Automated Regression Test

```text
tests/test_testbox_runtime.py::test_tbx_emp_zerohours_001_recognises_zero_hours_contract_and_sources
```

## TBX-EMP-ZEROHOURS-002

**Pattern:** Context-aware governed follow-up

### Dialogue

```text
User: мне предлогают заключить нулевой контракт что это значит
User: обьясни
```

### Required Behavior

- The second message must not fall back to generic chat.
- The previous regulated topic must be reused.
- Audit must include `CONTEXT_REUSED` and `FOLLOW_UP_RESOLVED`.
- The response must remain source-bound to `employment_contract`.

### Automated Regression Test

```text
tests/test_testbox_runtime.py::test_tbx_emp_zerohours_002_short_follow_up_reuses_previous_conversation_topic
```

## TBX-BUS-COOP-UA-001

**Pattern:** Focused follow-up within a governed business orientation case

### Dialogue

```text
User: хочу открыть компанию по производству источников хранения электричества
User: cooperatie UA обьясни более подробно
```

### Required Behavior

- The second message must resolve to intent `explain_cooperative_ua`.
- It must not repeat the broad business-formation answer.
- Retrieval must focus on the official cooperative source.
- The answer must explain `UA`, `BA`, `WA`, member liability and possible director liability.

### Automated Regression Test

```text
tests/test_testbox_runtime.py::test_tbx_bus_coop_ua_001_focused_follow_up_does_not_repeat_general_structure_answer
```
