#!/bin/bash
# Package Report Generator for distribution

VERSION="1.0.0"
PACKAGE_NAME="Report_Generator_v${VERSION}"
PACKAGE_DIR="${PACKAGE_NAME}"

echo "Creating distribution package..."

# Create package directory
mkdir -p "${PACKAGE_DIR}"

# Copy executable
if [ -d "dist/Report Generator.app" ]; then
    # Mac app bundle
    cp -r "dist/Report Generator.app" "${PACKAGE_DIR}/"
    echo "✓ Copied Mac app bundle"
fi

# Copy standalone executable
if [ -f "dist/kpr-report-generator" ]; then
    cp "dist/kpr-report-generator" "${PACKAGE_DIR}/"
    chmod +x "${PACKAGE_DIR}/kpr-report-generator"
    echo "✓ Copied standalone executable"
fi

# Copy example data
cp tests/fixtures/mock_data.csv "${PACKAGE_DIR}/example_data.csv"
echo "✓ Copied example data"

# Create QUICKSTART.txt
cat > "${PACKAGE_DIR}/QUICKSTART.txt" << 'EOF'
REPORT GENERATOR - QUICK START
==============================

WHAT IT DOES:
Generates weekly Key Priorities Reports from CSV exports.

HOW TO USE:

1. Export CSV from your data source
   - Open your Key Priorities view
   - Click "..." menu → "Download CSV"
   - Save the file

2. Run the generator:

   Option A - Using Mac App (Easiest):
   - Double-click "Report Generator.app"
   - Follow the prompts

   Option B - Using Terminal:
   - Open Terminal
   - Navigate to this folder
   - Run: ./kpr-report-generator generate --report kpr --csv YOUR_FILE.csv --email

3. Review the draft email
   - Mac Mail will open with your report
   - Review and send ("Message" → "Send Again")

NEED HELP?
- Check the project documentation
- Submit an issue on GitHub

EOF

echo "✓ Created QUICKSTART.txt"

# Create ZIP archive
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_DIR}"
echo "✓ Created ${PACKAGE_NAME}.zip"

echo ""
echo "Package ready: ${PACKAGE_NAME}.zip"
echo "Contents:"
ls -lh "${PACKAGE_DIR}"