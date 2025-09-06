# SHAB Publication Types Guide

This guide explains the different types of SHAB publications and how to handle them in your auction platform.

## 📋 Publication Types

### **SB01 - Schuldbetreibung (Debt Collection/Auctions)**
- **Purpose**: Contains auction and debt collection information
- **Contains**: Auctions, debtors, auction objects, contacts
- **Use Case**: ✅ **Perfect for your auction platform**
- **Example**: Property auctions, debt collection proceedings

### **HR02 - Handelsregister (Commercial Register)**
- **Purpose**: Company registration and business information
- **Contains**: Company details, registration office contacts
- **Use Case**: ❌ **Not relevant for auctions**
- **Example**: New company registrations, business changes

### **HR01 - Handelsregister (Commercial Register - Different Version)**
- **Purpose**: Similar to HR02 but different schema version
- **Contains**: Company details, registration office contacts
- **Use Case**: ❌ **Not relevant for auctions**

## 🔍 How to Identify Publication Types

### **From XML Content**
```xml
<!-- SB01 (Auction) Publication -->
<SB01:publication xmlns:SB01="https://shab.ch/shab/SB01-export">

<!-- HR02 (Commercial Register) Publication -->
<HR02:publication xmlns:HR02="https://shab.ch/shab/HR02-export">
```

### **From URL Structure**
```
https://www.shab.ch/api/v1/publications/{id}/xml
```

### **From Publication Metadata**
- **Rubric**: `SB` = Schuldbetreibung (Auctions)
- **Rubric**: `HR` = Handelsregister (Commercial Register)
- **SubRubric**: `SB01` = Debt Collection/Auctions
- **SubRubric**: `HR02` = Commercial Register

## 🛠️ Solutions for Your Platform

### **Option 1: Use Enhanced Bootstrap Script (Recommended)**

The enhanced bootstrap script automatically detects publication types and only processes auction publications:

```bash
# Use the enhanced bootstrap script
python scripts/enhanced_bootstrap.py your_publication_ids.txt
```

**Features:**
- ✅ Automatically detects publication types
- ✅ Only processes SB01 (auction) publications
- ✅ Skips non-auction publications with clear logging
- ✅ Provides detailed statistics

### **Option 2: Filter Publication IDs Manually**

Create a list of only auction publication IDs:

```bash
# Create auction-only publication list
echo "6048b37e-2062-4bc6-a4d9-66d472f3cc2d" > auction_publications.txt
echo "c42e67af-486d-44f4-8c6e-0ad03538770d" >> auction_publications.txt
echo "bb0b8622-803e-413e-8d71-bb6da17f5b0c" >> auction_publications.txt

# Use regular bootstrap script
python scripts/bootstrap_database.py auction_publications.txt
```

### **Option 3: Pre-filter with API**

You can filter publications by type using the SHAB API before processing:

```bash
# Example: Get only SB01 publications
curl "https://www.shab.ch/api/v1/publications?rubric=SB&subRubric=SB01"
```

## 📊 Expected Results by Publication Type

### **SB01 Publications (Auctions)**
```
✅ Publications: 1
✅ Auctions: 1
✅ Debtors: 1
✅ Contacts: 1
✅ Auction Objects: 1
```

### **HR02 Publications (Commercial Register)**
```
✅ Publications: 1
❌ Auctions: 0
❌ Debtors: 0
✅ Contacts: 1
❌ Auction Objects: 0
```

## 🔧 Troubleshooting

### **Issue: Missing Auction Data**
**Symptoms:**
- Publications exist but no auctions/debtors
- Only contacts are populated

**Cause:**
- Publication is not an SB01 type
- Publication is HR02 (commercial register)

**Solution:**
```bash
# Use enhanced bootstrap script
python scripts/enhanced_bootstrap.py

# Or filter for SB01 publications only
python scripts/bootstrap_database.py auction_publication_ids.txt
```

### **Issue: Mixed Publication Types**
**Symptoms:**
- Some publications have auction data, others don't
- Inconsistent record counts

**Cause:**
- Publication list contains mixed types (SB01 + HR02)

**Solution:**
```bash
# Check publication types first
python scripts/enhanced_bootstrap.py --analyze-only

# Then process only auction publications
python scripts/enhanced_bootstrap.py auction_only_ids.txt
```

## 📈 Best Practices

### **For Development**
1. **Use enhanced bootstrap script** for mixed publication lists
2. **Create separate lists** for different publication types
3. **Always check publication types** before processing
4. **Use cleanup scripts** to remove test data

### **For Production**
1. **Filter publications by type** before processing
2. **Use SB01 publications only** for auction platform
3. **Monitor processing logs** for skipped publications
4. **Set up alerts** for unexpected publication types

### **For Data Quality**
1. **Validate publication types** before bulk processing
2. **Keep separate databases** for different publication types
3. **Document publication sources** and types
4. **Regular cleanup** of non-relevant data

## 🎯 Recommended Workflow

```bash
# 1. Get publication IDs from SHAB search
# (Filter for SB01 publications if possible)

# 2. Use enhanced bootstrap script
python scripts/enhanced_bootstrap.py mixed_publications.txt

# 3. Check results
python scripts/cleanup_database.py --mode stats

# 4. Clean up if needed
python scripts/quick_cleanup.py

# 5. Process only auction publications
python scripts/enhanced_bootstrap.py auction_publications.txt
```

## 📚 Additional Resources

- **SHAB API Documentation**: https://www.shab.ch/api/v1/
- **XML Schema**: https://amtsblattportal.ch/api/v1/schemas/shab/1.24/
- **Publication Types**: Check the `rubric` and `subRubric` fields in XML metadata

## 🔄 Integration with Your Platform

The enhanced bootstrap script integrates seamlessly with your existing system:

- ✅ Uses the same SHAB parser
- ✅ Uses the same storage functions
- ✅ Uses the same database models
- ✅ Provides detailed logging and statistics
- ✅ Handles errors gracefully
- ✅ Compatible with cleanup scripts

This ensures you only populate your auction platform with relevant auction data while avoiding commercial register information that doesn't belong in your system.
