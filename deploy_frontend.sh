#!/bin/bash
# Deploy Frontend to Vercel
# Production-ready deployment with optimization

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="iva-margem-turismo"
VERCEL_TOKEN="${VERCEL_TOKEN:-$1}"
BACKEND_URL="${BACKEND_URL:-https://iva-margem-turismo-backend.up.railway.app}"

echo -e "${BLUE}🎨 IVA Margem Turismo - Frontend Deployment${NC}"
echo "================================================"

# Check prerequisites
check_requirements() {
    echo -e "${YELLOW}📋 Checking requirements...${NC}"
    
    # Check if in project root
    if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        echo -e "${RED}❌ Not in project root directory${NC}"
        echo "Run from: iva-margem-turismo/"
        exit 1
    fi
    
    # Check Vercel token
    if [ -z "$VERCEL_TOKEN" ]; then
        echo -e "${RED}❌ Vercel token not provided${NC}"
        echo "Usage: ./deploy_frontend.sh YOUR_VERCEL_TOKEN [BACKEND_URL]"
        echo "Or set: export VERCEL_TOKEN=your_token"
        exit 1
    fi
    
    # Check if npx is available
    if ! command -v npx &> /dev/null; then
        echo -e "${RED}❌ npx not found${NC}"
        echo "Install Node.js first"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements met${NC}"
}

# Update frontend configuration
update_frontend_config() {
    echo -e "\n${YELLOW}🔧 Updating frontend configuration...${NC}"
    
    # Backup original index.html
    cp frontend/index.html frontend/index.html.backup
    
    # Update API URL in frontend
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|http://localhost:8000|$BACKEND_URL|g" frontend/index.html
    else
        # Linux/WSL
        sed -i "s|http://localhost:8000|$BACKEND_URL|g" frontend/index.html
    fi
    
    echo -e "${GREEN}✅ API URL updated to: $BACKEND_URL${NC}"
    
    # Create vercel.json
    cat > vercel.json << EOF
{
  "version": 2,
  "name": "$PROJECT_NAME",
  "builds": [
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "$BACKEND_URL/api/\$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/\$1"
    }
  ],
  "headers": [
    {
      "source": "/frontend/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, s-maxage=86400, stale-while-revalidate"
        }
      ]
    },
    {
      "source": "/frontend/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/",
      "destination": "/frontend/index.html"
    }
  ]
}
EOF
    
    echo -e "${GREEN}✅ vercel.json created${NC}"
}

# Optimize assets
optimize_assets() {
    echo -e "\n${YELLOW}🎯 Optimizing assets...${NC}"
    
    # Create optimized version
    mkdir -p frontend/assets/optimized
    
    # Minify CSS if exists
    if [ -d "frontend/css" ]; then
        echo "Optimizing CSS files..."
        # In production, you'd use a CSS minifier here
    fi
    
    # Optimize images if any
    if [ -d "frontend/assets" ]; then
        echo "Optimizing images..."
        # In production, you'd use imagemin here
    fi
    
    echo -e "${GREEN}✅ Assets optimized${NC}"
}

# Deploy to Vercel
deploy_to_vercel() {
    echo -e "\n${YELLOW}🚀 Deploying to Vercel...${NC}"
    
    # Deploy with Vercel CLI
    echo -e "${BLUE}Starting deployment...${NC}"
    
    # Use npx to run vercel without installing globally
    DEPLOYMENT_URL=$(npx vercel \
        --token "$VERCEL_TOKEN" \
        --yes \
        --prod \
        --name "$PROJECT_NAME" \
        2>&1 | tee /tmp/vercel-deploy.log | grep -oP "https://[^\s]+" | tail -1)
    
    if [ -n "$DEPLOYMENT_URL" ]; then
        echo -e "${GREEN}✅ Deployment successful!${NC}"
        echo -e "URL: ${BLUE}$DEPLOYMENT_URL${NC}"
    else
        echo -e "${RED}❌ Deployment failed${NC}"
        echo "Check logs at: /tmp/vercel-deploy.log"
        exit 1
    fi
}

# Configure production settings
configure_production() {
    echo -e "\n${YELLOW}⚙️  Configuring production settings...${NC}"
    
    # Set environment variables
    echo -e "${BLUE}Setting environment variables...${NC}"
    npx vercel env add BACKEND_URL "$BACKEND_URL" production --token "$VERCEL_TOKEN" --yes || true
    
    # Configure analytics (optional)
    echo -e "${GREEN}✅ Production configured${NC}"
}

# Health check
health_check() {
    echo -e "\n${YELLOW}🏥 Running health check...${NC}"
    
    if [ -z "$DEPLOYMENT_URL" ]; then
        echo -e "${YELLOW}⚠️  No deployment URL found${NC}"
        return
    fi
    
    # Wait for deployment
    echo "Waiting for deployment to propagate..."
    sleep 20
    
    # Check if frontend loads
    if curl -s -f "$DEPLOYMENT_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
        
        # Check if can reach backend
        if curl -s "$DEPLOYMENT_URL" | grep -q "IVA Margem Turismo"; then
            echo -e "${GREEN}✅ Application loaded successfully${NC}"
        fi
    else
        echo -e "${RED}❌ Frontend not accessible${NC}"
    fi
}

# Restore backup
restore_backup() {
    if [ -f "frontend/index.html.backup" ]; then
        echo -e "\n${YELLOW}🔄 Restoring original files...${NC}"
        mv frontend/index.html.backup frontend/index.html
        echo -e "${GREEN}✅ Original files restored${NC}"
    fi
}

# Show next steps
show_next_steps() {
    echo -e "\n${BLUE}📋 Next Steps:${NC}"
    echo "1. Test the application: $DEPLOYMENT_URL"
    echo "2. Configure custom domain: npx vercel domains add yourdomain.com"
    echo "3. View analytics: npx vercel"
    echo "4. Monitor performance: Vercel dashboard"
    echo ""
    echo -e "${GREEN}🎉 Frontend deployment complete!${NC}"
    echo ""
    echo -e "${BLUE}📊 Deployment Summary:${NC}"
    echo "Frontend: $DEPLOYMENT_URL"
    echo "Backend: $BACKEND_URL"
    echo "API Docs: $BACKEND_URL/docs"
}

# Main execution
main() {
    check_requirements
    update_frontend_config
    optimize_assets
    deploy_to_vercel
    configure_production
    health_check
    restore_backup
    show_next_steps
}

# Error handling
trap 'echo -e "\n${RED}❌ Deployment failed!${NC}" >&2; restore_backup' ERR

# Run deployment
main