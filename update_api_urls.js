/**
 * Helper script to update API URLs in frontend files
 * Run this before deploying to update production API URL
 * 
 * Usage: node update_api_urls.js https://your-app.onrender.com
 */

const fs = require('fs');
const path = require('path');

// Get API URL from command line argument
const apiUrl = process.argv[2];

if (!apiUrl) {
    console.error('❌ Please provide API URL as argument');
    console.log('Usage: node update_api_urls.js https://your-app.onrender.com');
    process.exit(1);
}

// Ensure URL doesn't end with /api (we add it in the code)
const baseUrl = apiUrl.replace(/\/api\/?$/, '');
const fullApiUrl = `${baseUrl}/api`;

console.log(`🔄 Updating API URLs to: ${fullApiUrl}`);

// Files to update
const files = [
    { path: 'events_api.js', pattern: /const API_BASE_URL = .*?;/ },
    { path: 'list_event.js', pattern: /const API_BASE = .*?;/ }
];

files.forEach(file => {
    const filePath = path.join(__dirname, file.path);
    
    if (!fs.existsSync(filePath)) {
        console.warn(`⚠️  File not found: ${file.path}`);
        return;
    }
    
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Update the API URL
    if (file.path === 'events_api.js') {
        content = content.replace(
            /const API_BASE_URL = .*?;/,
            `const API_BASE_URL = '${fullApiUrl}';`
        );
    } else if (file.path === 'list_event.js') {
        content = content.replace(
            /const API_BASE = .*?;/,
            `const API_BASE = '${fullApiUrl}';`
        );
    }
    
    if (content !== originalContent) {
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`✅ Updated ${file.path}`);
    } else {
        console.log(`ℹ️  No changes needed in ${file.path}`);
    }
});

console.log('\n✨ Done! API URLs updated.');
