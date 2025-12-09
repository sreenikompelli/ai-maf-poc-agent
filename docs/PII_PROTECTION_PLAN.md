# PII Protection in Azure AI Foundry - Correct Approach

## ✅ You're Right! No Separate Service Needed

**Azure AI Foundry has BUILT-IN PII protection** as part of its RAI (Responsible AI) policies!

## What Azure AI Foundry Provides

### Built-in PII Detection
- **Automatic PII detection** in prompts and responses
- **50+ PII types** supported
- **Two modes**:
  - **Annotate**: Flag PII but allow content
  - **Annotate and Block**: Block entire output if PII detected
- **Integration with Microsoft Purview** for monitoring

### PII Types Supported
- Names, addresses, phone numbers
- Email addresses
- Social Security Numbers
- Passport numbers
- Financial information
- Protected Health Information (PHI)

## Correct Implementation: Extend RAI Policy

### Current Structure
```
infrastructure/modules/guardrails/
└── content_filter.bicep  ← Extend this!
```

### Updated Bicep Template

```bicep
// infrastructure/modules/guardrails/content_filter.bicep
resource contentFilter 'Microsoft.CognitiveServices/accounts/raiPolicies@2025-04-01-preview' = {
  parent: aiAccount
  name: filterName
  properties: {
    mode: 'Default'
    basePolicyName: 'Microsoft.Default'
    
    // Existing: Harmful content filters
    contentFilters: [
      // ... hate, sexual, violence, self-harm filters
    ]
    
    // NEW: PII filters
    piiFilters: [
      {
        category: 'Email'
        mode: 'AnnotateAndBlock'  // or 'Annotate'
        enabled: true
      }
      {
        category: 'PhoneNumber'
        mode: 'AnnotateAndBlock'
        enabled: true
      }
      {
        category: 'SSN'
        mode: 'AnnotateAndBlock'
        enabled: true
      }
      {
        category: 'CreditCard'
        mode: 'AnnotateAndBlock'
        enabled: true
      }
      {
        category: 'Address'
        mode: 'Annotate'  // Flag but don't block
        enabled: true
      }
    ]
  }
}
```

### Updated Parameters

```bicep
// infrastructure/parameters/guardrails.bicepparam
using '../modules/guardrails/content_filter.bicep'

param projectName = 'adusa-poc-agent'
param filterName = 'content-filter'

// Existing content filter config
param contentFilterConfig = {
  hate: { enabled: true, severity: 'medium', blocking: true }
  sexual: { enabled: true, severity: 'medium', blocking: true }
  violence: { enabled: true, severity: 'medium', blocking: true }
  selfHarm: { enabled: true, severity: 'high', blocking: true }
}

// NEW: PII filter config
param piiFilterConfig = {
  email: { enabled: true, mode: 'AnnotateAndBlock' }
  phoneNumber: { enabled: true, mode: 'AnnotateAndBlock' }
  ssn: { enabled: true, mode: 'AnnotateAndBlock' }
  creditCard: { enabled: true, mode: 'AnnotateAndBlock' }
  address: { enabled: true, mode: 'Annotate' }
  passport: { enabled: true, mode: 'AnnotateAndBlock' }
  name: { enabled: false, mode: 'Annotate' }  // Often too many false positives
}

param tags = {
  environment: 'nonprod'
  managedBy: 'devops'
  project: 'ai-agents'
  purpose: 'content-filtering-and-pii'
}
```

## Implementation Steps

### Phase 1: Update Bicep Template (30 min)
- [ ] Add PII filter support to `content_filter.bicep`
- [ ] Add parameters for PII categories
- [ ] Configure modes (Annotate vs AnnotateAndBlock)

### Phase 2: Update Parameters (15 min)
- [ ] Add PII configuration to `guardrails.bicepparam`
- [ ] Choose which PII types to enable
- [ ] Set appropriate modes

### Phase 3: Deploy (5 min)
```bash
python3 scripts/deploy_guardrails.py nonprod
```

### Phase 4: Test (30 min)
- [ ] Test with sample PII data
- [ ] Verify blocking works
- [ ] Check annotation mode
- [ ] Review in Azure portal

### Phase 5: Monitor (Ongoing)
- [ ] Check Microsoft Purview for PII signals
- [ ] Review blocked requests
- [ ] Adjust sensitivity as needed

## PII Filter Modes

### Annotate Mode
- **Behavior**: Flags PII but allows content through
- **Use case**: Non-critical PII (addresses, names)
- **Example**:
  ```
  Input: "My address is 123 Main St"
  Output: "My address is 123 Main St"
  Metadata: { pii_detected: ['Address'] }
  ```

### Annotate and Block Mode
- **Behavior**: Blocks entire output if PII detected
- **Use case**: Critical PII (SSN, credit cards)
- **Example**:
  ```
  Input: "My SSN is 123-45-6789"
  Output: [BLOCKED - PII DETECTED]
  Error: "Content contains sensitive information"
  ```

## Comparison: Built-in vs Separate Service

| Aspect | Built-in (Foundry) | Separate (AI Language) |
|--------|-------------------|------------------------|
| **Cost** | ✅ Included | ❌ Extra $2/1000 records |
| **Setup** | ✅ Just update Bicep | ❌ Deploy new service |
| **Integration** | ✅ Automatic | ❌ Manual code changes |
| **Maintenance** | ✅ Managed by Foundry | ❌ Separate service |
| **Configuration** | ✅ RAI policy | ❌ API calls |

**Winner**: Built-in Foundry PII protection! 🏆

## Updated Timeline

| Phase | Task | Time |
|-------|------|------|
| 1 | Update Bicep template | 30 min |
| 2 | Update parameters | 15 min |
| 3 | Deploy | 5 min |
| 4 | Test | 30 min |
| 5 | Document | 15 min |

**Total**: ~1.5 hours (vs 6 hours for separate service!)

## Example Configuration

### Conservative (Recommended for Start)
```bicep
param piiFilterConfig = {
  ssn: { enabled: true, mode: 'AnnotateAndBlock' }
  creditCard: { enabled: true, mode: 'AnnotateAndBlock' }
  passport: { enabled: true, mode: 'AnnotateAndBlock' }
  email: { enabled: true, mode: 'Annotate' }
  phoneNumber: { enabled: true, mode: 'Annotate' }
}
```

### Strict (For Sensitive Applications)
```bicep
param piiFilterConfig = {
  ssn: { enabled: true, mode: 'AnnotateAndBlock' }
  creditCard: { enabled: true, mode: 'AnnotateAndBlock' }
  passport: { enabled: true, mode: 'AnnotateAndBlock' }
  email: { enabled: true, mode: 'AnnotateAndBlock' }
  phoneNumber: { enabled: true, mode: 'AnnotateAndBlock' }
  address: { enabled: true, mode: 'AnnotateAndBlock' }
  name: { enabled: true, mode: 'Annotate' }
}
```

## Benefits of Built-in Approach

1. ✅ **No extra cost** - included in Foundry
2. ✅ **Simpler architecture** - one RAI policy
3. ✅ **Automatic integration** - works with all agents
4. ✅ **Unified management** - content + PII in one place
5. ✅ **Microsoft Purview integration** - built-in monitoring
6. ✅ **No code changes** - infrastructure only

## Next Steps

1. **Update `content_filter.bicep`** to add PII filters
2. **Update `guardrails.bicepparam`** with PII configuration
3. **Redeploy** using existing script
4. **Test** with sample PII data
5. **Monitor** in Azure portal and Purview

## Questions Answered

1. ✅ **Do I need Azure AI Language service?** NO! Use built-in Foundry PII
2. ✅ **Is it part of RAI policies?** YES! Extend existing policy
3. ✅ **Extra cost?** NO! Included in Foundry
4. ✅ **Code changes needed?** NO! Just Bicep updates
5. ✅ **How to monitor?** Microsoft Purview integration

## Recommendation

**Use Azure AI Foundry's built-in PII protection** by extending your existing RAI policy. It's:
- Simpler
- Cheaper (free)
- Better integrated
- Easier to maintain

No need for a separate Azure AI Language service! 🎉
