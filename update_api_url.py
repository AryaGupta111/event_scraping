"""
Quick script to update API URL in frontend files
Run this after deploying to Render
"""

import re
import sys

def update_api_url(render_url):
    """Update API URL in JavaScript files"""
    
    # Files to update
    files = ['events_api.js', 'list_event.js']
    
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern to find API_BASE_URL
            pattern = r"const API_BASE_URL = .*?'https://.*?\.onrender\.com/api'"
            
            # New URL
            replacement = f"const API_BASE_URL = (typeof window !== 'undefined' && window.location.hostname === 'localhost') \n    ? 'http://localhost:5000/api' \n    : '{render_url}/api'"
            
            # Replace
            if 'API_BASE_URL' in content:
                # Find the full declaration
                old_pattern = r"const API_BASE_URL = \(typeof window.*?\);?"
                content = re.sub(old_pattern, replacement + ';', content, flags=re.DOTALL)
                
                # Write back
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {filename}")
            else:
                print(f"⚠️  API_BASE_URL not found in {filename}")
                
        except FileNotFoundError:
            print(f"⚠️  {filename} not found, skipping...")
        except Exception as e:
            print(f"❌ Error updating {filename}: {e}")
    
    print(f"\n✅ API URL updated to: {render_url}")
    print("\nNext steps:")
    print("1. Test locally: python api_server.py")
    print("2. Commit changes: git add . && git commit -m 'Update API URL'")
    print("3. Push to GitHub: git push")
    print("4. Deploy frontend to Vercel")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_api_url.py <your-render-url>")
        print("Example: python update_api_url.py https://crypto-events-api.onrender.com")
        sys.exit(1)
    
    render_url = sys.argv[1].rstrip('/')
    update_api_url(render_url)
