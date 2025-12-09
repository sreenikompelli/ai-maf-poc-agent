# Base vs Environment Overrides - Examples

## Overview

This document shows concrete examples of how base configuration + environment overrides work.

## File Structure

```
infrastructure/parameters/guardrails/
├── base.bicepparam    # Shared defaults for ALL environments
├── dev.bicepparam     # Development overrides (permissive)
├── test.bicepparam    # Testing overrides (moderate)
└── prod.bicepparam    # Production overrides (strict)
```

## Configuration Comparison

### Content Filters

| Filter | Base (Default) | Dev Override | Prod Override | Reason |
|--------|---------------|--------------|---------------|---------|
| **Hate** |
| Severity | `medium` | `low` 🔄 | `high` 🔄 | Dev needs flexibility, Prod needs protection |
| Blocking | `true` | `false` 🔄 | `true` ✅ | Dev annotates only, Prod blocks |
| **Sexual** |
| Severity | `medium` | `low` 🔄 | `high` 🔄 | Same reasoning as hate |
| Blocking | `true` | `false` 🔄 | `true` ✅ | Same reasoning as hate |
| **Violence** |
| Severity | `medium` | `low` 🔄 | `high` 🔄 | Same reasoning as hate |
| Blocking | `true` | `false` 🔄 | `true` ✅ | Same reasoning as hate |
| **Self-Harm** |
| Severity | `high` | `medium` 🔄 | `high` ✅ | Always strict, slightly relaxed in dev |
| Blocking | `true` | `true` ✅ | `true` ✅ | NEVER allow self-harm content |

### PII Filters

| PII Type | Base (Default) | Dev Override | Prod Override | Reason |
|----------|---------------|--------------|---------------|---------|
| **SSN** |
| Mode | `AnnotateAndBlock` | `Annotate` 🔄 | `AnnotateAndBlock` ✅ | Dev needs to test, Prod blocks |
| **Credit Card** |
| Mode | `AnnotateAndBlock` | `Annotate` 🔄 | `AnnotateAndBlock` ✅ | Same as SSN |
| **Email** |
| Mode | `Annotate` | `Annotate` ✅ | `AnnotateAndBlock` 🔄 | Prod is stricter |
| **Phone** |
| Mode | `Annotate` | `Annotate` ✅ | `AnnotateAndBlock` 🔄 | Prod is stricter |
| **Name** |
| Enabled | `false` | `true` 🔄 | `true` 🔄 | Disabled by default (false positives) |
| Mode | `Annotate` | `Annotate` ✅ | `Annotate` ✅ | Only annotate (too many false positives) |

### Prompt Shields

| Shield | Base (Default) | Dev Override | Prod Override | Reason |
|--------|---------------|--------------|---------------|---------|
| **Jailbreak** |
| Blocking | `true` | `false` 🔄 | `true` ✅ | Dev needs to test prompts |
| **Indirect Attack** |
| Blocking | `true` | `false` 🔄 | `true` ✅ | Dev needs to test prompts |

## Legend

- ✅ **KEEP**: Uses base value (no override)
- 🔄 **OVERRIDE**: Changes base value
- 🆕 **NEW**: Adds new setting not in base

## Real-World Examples

### Example 1: Testing Hate Speech Detection in Dev

**Scenario**: Developer wants to test how the system handles borderline hate speech

**Base Config**:
```bicep
hate: { severity: 'medium', blocking: true }
```

**Dev Override**:
```bicep
hate: { severity: 'low', blocking: false }  // 🔄 More permissive
```

**Result**: 
- Dev can test with borderline content
- System annotates but doesn't block
- Developer sees what would be flagged in prod

### Example 2: Email Handling Across Environments

**Scenario**: Different email handling needs per environment

**Base Config**:
```bicep
email: { mode: 'Annotate' }  // Just flag, don't block
```

**Dev Override**:
```bicep
email: { mode: 'Annotate' }  // ✅ Keep base (same behavior)
```

**Prod Override**:
```bicep
email: { mode: 'AnnotateAndBlock' }  // 🔄 Block in production
```

**Result**:
- Dev: Emails are flagged but allowed (for testing)
- Prod: Emails are blocked (data protection)

### Example 3: SSN Protection

**Scenario**: Critical PII needs different handling

**Base Config**:
```bicep
ssn: { mode: 'AnnotateAndBlock' }  // Block by default
```

**Dev Override**:
```bicep
ssn: { mode: 'Annotate' }  // 🔄 Don't block (need to test)
```

**Prod Override**:
```bicep
ssn: { mode: 'AnnotateAndBlock' }  // ✅ Keep base (always block)
```

**Result**:
- Dev: Can test with fake SSNs, system annotates
- Prod: Real SSNs are immediately blocked

## Configuration Philosophy

### Base Configuration
**Purpose**: Sensible defaults that work for most environments

**Characteristics**:
- Balanced severity (medium)
- Block harmful content
- Annotate moderate PII
- Block critical PII

### Dev Configuration
**Purpose**: Enable testing and development

**Characteristics**:
- Low severity (permissive)
- Annotate instead of block
- Enable all PII types for testing
- Allow prompt engineering experiments

**Trade-off**: Less protection for more flexibility

### Prod Configuration
**Purpose**: Maximum protection for real users

**Characteristics**:
- High severity (strict)
- Block everything suspicious
- Zero tolerance for PII
- Full attack protection

**Trade-off**: Less flexibility for more safety

## How Overrides Work

### Inheritance Pattern

```
Base Config (Defaults)
    ↓
Environment Config (Overrides)
    ↓
Final Deployed Config
```

### Example Flow

1. **Base defines**:
   ```bicep
   hate: { severity: 'medium', blocking: true }
   ```

2. **Dev overrides**:
   ```bicep
   hate: { severity: 'low', blocking: false }
   ```

3. **Final dev config**:
   ```bicep
   hate: { severity: 'low', blocking: false }  // Dev values win
   ```

4. **Prod doesn't override**:
   ```bicep
   hate: { severity: 'high', blocking: true }  // Prod values win
   ```

## When to Override

### Always Override
- ✅ Environment-specific tags
- ✅ Severity levels (dev vs prod)
- ✅ Blocking behavior (dev vs prod)

### Sometimes Override
- ⚠️  Enabled/disabled flags
- ⚠️  PII detection modes
- ⚠️  Experimental features

### Never Override
- ❌ Self-harm blocking (always strict)
- ❌ Critical security settings
- ❌ Compliance requirements

## Benefits of This Approach

1. **DRY Principle**: Don't repeat yourself
   - Define once in base
   - Override only what's different

2. **Clear Intent**: Overrides show what's special about each environment
   - Easy to see dev is more permissive
   - Easy to see prod is stricter

3. **Maintainability**: Update base, all environments benefit
   - Add new PII type in base
   - Automatically applies to all envs
   - Override only if needed

4. **Safety**: Prod defaults to strict
   - If you forget to override, prod is safe
   - Dev explicitly opts into permissiveness

## Common Patterns

### Pattern 1: Graduated Strictness
```
Dev:  low severity, annotate only
Test: medium severity, selective blocking
Prod: high severity, block everything
```

### Pattern 2: Feature Flags
```
Dev:  experimental features enabled
Prod: experimental features disabled
```

### Pattern 3: PII Handling
```
Dev:  all PII types enabled, annotate mode
Prod: critical PII blocked, moderate PII annotated
```

## Next Steps

1. Review base.bicepparam - adjust defaults if needed
2. Review dev.bicepparam - ensure it's permissive enough for testing
3. Review prod.bicepparam - ensure it's strict enough for production
4. Deploy to dev first: `python3 scripts/deploy_guardrails.py dev`
5. Test thoroughly in dev
6. Deploy to prod: `python3 scripts/deploy_guardrails.py prod`
