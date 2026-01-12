# Report Generator - User Guide

**Version 1.0.0**
**Last Updated:** December 2024

---

## Table of Contents

1. [Introduction](#introduction)
2. [What You Need](#what-you-need)
3. [Getting Started](#getting-started)
4. [Using the Generator](#using-the-generator)
5. [Customizing the Report](#customizing-the-report)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Introduction

The Report Generator automates the creation of weekly Key Priorities Reports. Instead of manually formatting the report each week, you can:

1. Export CSV from your data source (Airtable, spreadsheet, etc.)
2. Run the generator
3. Get a beautifully formatted email draft ready to send

**What it does:**
- Loads data from CSV export
- Validates and transforms the data
- Generates formatted HTML report
- Opens pre-filled email draft in Mac Mail
- Groups deliverables by status (Off Track, At Risk, On Track, Complete)
- Includes all team leads, achievements, and risks

**Time savings:** ~30-45 minutes per week

---

## What You Need

### Required
- **Mac computer** (macOS 10.14 or later)
- **Mac Mail** configured with your email account
- **Access** to your data source (Airtable, spreadsheet, etc.)
- **Report Generator** executable

### Optional
- Terminal familiarity (for advanced usage)

---

## Getting Started

### First-Time Setup

1. **Download the generator package**
   - You should receive: `Report_Generator_v1.0.zip`
   - Unzip it to a location you'll remember (e.g., `Documents/`)

2. **Verify Mac Mail is configured**
   - Open Mac Mail
   - Ensure your email account is set up
   - Send yourself a test email to confirm it works

3. **Grant automation permissions** (if prompted)
   - When you first run the generator, macOS may ask for permission
   - Go to: **System Settings → Privacy & Security → Automation**
   - Allow the generator to control Mac Mail

4. **Test with example data**
   - The package includes `example_data.csv`
   - Use this to verify everything works before using real data

---

## Using the Generator

### Method 1: Double-Click (Easiest)

**Perfect for weekly use when you just want to generate the report quickly.**

1. **Export CSV from your data source**
   - Open your Key Priorities view in Airtable (or other source)
   - Click the **"..."** menu (top right)
   - Select **"Download CSV"**
   - Save to your computer (note the location!)

2. **Launch the generator**
   - Navigate to your `Report_Generator_v1.0` folder
   - Double-click: **"Launch Report Generator.command"**
   - A Terminal window will open

3. **Provide the CSV file**
```
   Drag and drop your Airtable CSV file here, then press Enter:
   
   CSV file: _
```
   - Drag the CSV file from Finder into the Terminal window
   - Press **Enter**

4. **Wait for generation** (5-10 seconds)
```
   Loading data from /path/to/file.csv...
   ✓ Loaded 73 rows
   Validating data structure...
   ✓ Validation passed
   Transforming data...
   ✓ Transformed 73 deliverables
   Building report context...
   ✓ Context ready
   Rendering HTML template...
   ✓ Template rendered
   ✓ Report saved to outputs/kpr_report_2024-12-24.html
   
   ✓ EML draft opened
```

5. **Review the email draft**
   - Mac Mail will open automatically
   - You'll see a draft email with:
     - **To:** Your configured recipients
     - **Subject:** Weekly Key Priorities Report - [Date]
     - **Body:** Your formatted report

6. **Review and send**
   - Scroll through to verify everything looks correct
   - Add any additional notes if needed
   - From the app menubar, select Message > Send Again 
   - Click **Send**

7. **Close the Terminal**
   - Press **Enter** to close the Terminal window

---

### Method 2: Command Line (Advanced)

**For power users who want more control.**

Open Terminal and navigate to the generator folder:
```bash
cd /path/to/Report_Generator_v1.0
```

#### Generate report only (no email)
```bash
./kpr-report-generator generate --report kpr --csv YOUR_FILE.csv
```

This creates the HTML file in `outputs/` but doesn't open email.

#### Generate with custom output location
```bash
./kpr-report-generator generate \
  --report kpr \
  --csv YOUR_FILE.csv \
  --output ~/Desktop/my_report.html
```

#### Generate and open email draft
```bash
./kpr-report-generator generate \
  --report kpr \
  --csv YOUR_FILE.csv \
  --email
```

#### List available reports
```bash
./kpr-report-generator list-reports
```

#### Show help
```bash
./kpr-report-generator --help
./kpr-report-generator generate --help
```

---

## Customizing the Report

### Changing Email Recipients

If you need to change who receives the report:

1. Open the generator folder
2. Right-click `kpr-report-generator` → **Show Package Contents** (if using .app)
3. Navigate to: `report_generator/reports/example_report/config.py`
4. Find the `EMAIL_CONFIG` section:
```python
EMAIL_CONFIG = {
    "to": ["your-team@example.com"],
    "cc": [],
    "subject": "Weekly Key Priorities Report - {date}",
}
```

5. Modify as needed
6. Save the file

**Note:** For packaged executables, contact the maintainer to rebuild with new settings.

### Changing Report Styling

The report template is located at:
`report_generator/reports/example_report/template.html`

You can modify:
- Colors (primary: `#00338D`, accent: `#FFD100`)
- Fonts
- Layout
- Section headers
- Footer text

After changes, rebuild the executable (see developer docs).

---

## Troubleshooting

### Email draft doesn't open

**Symptoms:** Report generates but Mac Mail doesn't open, or opens with blank message.

**Solutions:**
1. **Check Mac Mail is configured**
   - Open Mac Mail manually
   - Verify your email account works

2. **Grant automation permissions**
   - System Settings → Privacy & Security → Automation
   - Find the generator in the list
   - Ensure Mac Mail is checked

3. **Try the fallback**
   - If email doesn't open, check `outputs/` folder
   - Open the `.html` file in a browser
   - Copy/paste into email manually

### "File not found" error

**Symptoms:** 
```
✗ File not found: /path/to/file.csv
```

**Solutions:**
1. Verify the CSV file exists at the path you provided
2. Check for typos in the filename
3. Ensure the file has `.csv` extension
4. Try dragging the file directly into Terminal (removes path issues)

### Data validation warnings

**Symptoms:**
```
⚠ Warnings:
  - Missing expected columns: Initiative (L3)
```

**What it means:** The CSV is missing some columns, but the report will still generate.

**Solutions:**
1. Check your Airtable view includes all fields
2. Re-export with the correct view/filters
3. If intentional (field removed), the report adapts automatically

### "nan" appearing in report

**Symptoms:** Text shows "nan" instead of blank or proper values.

**What it means:** Empty cells in the CSV are being read as NaN (Not a Number).

**Solutions:**
1. Ensure empty cells in Airtable are truly empty (no spaces)
2. This is usually handled automatically by the generator
3. If persistent, contact the maintainer

### Executable won't run / Permission denied

**Symptoms:**
```
Permission denied: ./kpr-report-generator
```

**Solutions:**
```bash
chmod +x kpr-report-generator
chmod +x "Launch KPR Generator.command"
```

### Slow startup / Long delay

**Normal behavior:** The executable takes 5-10 seconds to start the first time.

**Why:** PyInstaller executables unpack dependencies on launch.

**Not a problem:** Just be patient! Subsequent runs may be faster.

---

## FAQ

### Q: Can I use this on Windows?

**A:** Not currently. The tool is built for macOS. Windows support could be added in the future.

### Q: Can I schedule this to run automatically?

**A:** Not currently. This requires manual CSV export from Airtable. Future versions could integrate with Airtable API for automation.

### Q: What if I need to generate multiple reports in one week?

**A:** Run the generator multiple times with different CSV exports. Each report gets timestamped automatically.

### Q: Can I customize the email subject or recipients?

**A:** Yes, but it requires modifying the configuration file (see "Customizing the Report" section above). For permanent changes, contact the maintainer to rebuild the executable.

### Q: Is my data secure?

**A:** Yes. The tool runs entirely on your local machine. No data is sent to external servers. The CSV file is processed locally and the HTML is generated locally.

### Q: What if Airtable changes their CSV format?

**A:** The generator includes data validation and will warn you if columns are missing. Minor changes are usually handled automatically. For major changes, contact the maintainer.

### Q: Can I add a new report type?

**A:** Yes! See `docs/ARCHITECTURE.md` for developer instructions on adding new report types.

### Q: Where are the generated reports saved?

**A:** By default, in the `outputs/` folder with timestamp in filename:
```
outputs/kpr_report_2024-12-24.html
```

You can specify a custom location with `--output` flag.

### Q: Can I preview the report before sending the email?

**A:** Yes! Generate without the `--email` flag, then open the HTML file in a browser:
```bash
./kpr-report-generator generate --report kpr --csv YOUR_FILE.csv
open outputs/kpr_report_2024-12-24.html
```

---

## Getting Help

### For Issues with the Tool
- Check the project's GitHub Issues page
- Review the README and ARCHITECTURE documentation

### For Data Source Issues
- Check your data source's documentation
- Ensure CSV export format matches expected structure

### For Mac Mail Issues
- Check System Preferences → Automation permissions
- Consult Apple's Mail documentation

---

## Appendix: CSV Export Checklist

Use this checklist each week to ensure a clean export:

- [ ] Open the correct Airtable view (Key Priorities)
- [ ] Verify all expected columns are visible
- [ ] Check date ranges/filters are correct
- [ ] Export as CSV (not Excel or other format)
- [ ] Save with clear filename (e.g., `KPR_2024-12-24.csv`)
- [ ] Note where you saved it for easy access
- [ ] Run the generator within 5 minutes (while data is fresh in mind)

---

**Version History:**
- v1.0.0 (Dec 2024) - Initial release