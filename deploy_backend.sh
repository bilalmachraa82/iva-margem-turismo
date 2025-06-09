#!/bin/bash
# Deploy Backend to Railway
# Expert deployment script with rollback capability

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="iva-margem-turismo-backend"
RAILWAY_TOKEN="${RAILWAY_TOKEN:-$1}"

echo -e "${BLUE}🚀 IVA Margem Turismo - Backend Deployment${NC}"
echo "================================================"

# Check prerequisites
check_requirements() {
    echo -e "${YELLOW}📋 Checking requirements...${NC}"
    
    # Check Railway CLI
    if ! command -v railway &> /dev/null; then
        echo -e "${RED}❌ Railway CLI not found${NC}"
        echo "Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if in backend directory
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ Not in backend directory${NC}"
        echo "Run from: iva-margem-turismo/backend/"
        exit 1
    fi
    
    # Check Railway token
    if [ -z "$RAILWAY_TOKEN" ]; then
        echo -e "${RED}❌ Railway token not provided${NC}"
        echo "Usage: ./deploy_backend.sh YOUR_RAILWAY_TOKEN"
        echo "Or set: export RAILWAY_TOKEN=your_token"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements met${NC}"
}

# Prepare deployment
prepare_deployment() {
    echo -e "\n${YELLOW}📦 Preparing deployment...${NC}"
    
    # Update database.py if migration was run
    if [ -f "database.py" ]; then
        echo -e "${GREEN}✅ database.py found${NC}"
    else
        echo -e "${YELLOW}⚠️  database.py not found - run migrate_to_postgres.py first${NC}"
    fi
    
    # Ensure Procfile exists
    if [ ! -f "Procfile" ]; then
        echo "web: python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
        echo -e "${GREEN}✅ Procfile created${NC}"
    fi
    
    # Create .env.example
    cat > .env.example << EOF
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require

# Redis Cache (optional)
REDIS_URL=redis://default:password@host:6379

# Environment
ENVIRONMENT=production
PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://iva-margem-turismo.vercel.app,http://localhost:3000

# Monitoring (optional)
SENTRY_DSN=https://xxx@sentry.io/xxx
EOF
    echo -e "${GREEN}✅ .env.example created${NC}"
}

# Deploy to Railway
deploy_to_railway() {
    echo -e "\n${YELLOW}🚂 Deploying to Railway...${NC}"
    
    # Login with token
    echo -e "${BLUE}Logging in to Railway...${NC}"
    railway login --token "$RAILWAY_TOKEN"
    
    # Check if project exists
    if railway status 2>/dev/null | grep -q "$PROJECT_NAME"; then
        echo -e "${GREEN}✅ Project exists, updating...${NC}"
    else
        echo -e "${BLUE}Creating new project...${NC}"
        railway init -n "$PROJECT_NAME"
    fi
    
    # Link to project
    railway link
    
    # Add PostgreSQL if not exists
    echo -e "\n${BLUE}Checking database...${NC}"
    if ! railway variables | grep -q "DATABASE_URL"; then
        echo -e "${YELLOW}Adding PostgreSQL plugin...${NC}"
        railway add
        echo -e "${GREEN}✅ PostgreSQL added${NC}"
    else
        echo -e "${GREEN}✅ Database already configured${NC}"
    fi
    
    # Set environment variables
    echo -e "\n${BLUE}Setting environment variables...${NC}"
    railway variables set \
        ENVIRONMENT=production \
        PYTHON_VERSION=3.9 \
        ALLOWED_ORIGINS="https://iva-margem-turismo.vercel.app"
    
    # Deploy
    echo -e "\n${BLUE}🚀 Deploying application...${NC}"
    railway up
    
    # Get deployment URL
    echo -e "\n${BLUE}Getting deployment info...${NC}"
    DEPLOY_URL=$(railway status | grep "Deployment URL" | awk '{print $3}')
    
    if [ -n "$DEPLOY_URL" ]; then
        echo -e "${GREEN}✅ Deployment successful!${NC}"
        echo -e "URL: ${BLUE}$DEPLOY_URL${NC}"
    else
        # Try to get domain
        DOMAIN=$(railway domain | grep -oP 'https://[^\s]+')
        if [ -n "$DOMAIN" ]; then
            echo -e "${GREEN}✅ Deployment successful!${NC}"
            echo -e "URL: ${BLUE}$DOMAIN${NC}"
            DEPLOY_URL=$DOMAIN
        fi
    fi
}

# Health check
health_check() {
    echo -e "\n${YELLOW}🏥 Running health check...${NC}"
    
    if [ -z "$DEPLOY_URL" ]; then
        echo -e "${YELLOW}⚠️  No deployment URL found, skipping health check${NC}"
        return
    fi
    
    # Wait for deployment to be ready
    echo "Waiting for deployment to be ready..."
    sleep 30
    
    # Check health endpoint
    if curl -s -f "$DEPLOY_URL/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed${NC}"
        
        # Check API docs
        if curl -s -f "$DEPLOY_URL/docs" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API documentation available${NC}"
        fi
    else
        echo -e "${RED}❌ Health check failed${NC}"
        echo "Check logs with: railway logs"
    fi
}

# Show next steps
show_next_steps() {
    echo -e "\n${BLUE}📋 Next Steps:${NC}"
    echo "1. Update frontend API URL to: $DEPLOY_URL"
    echo "2. Configure custom domain: railway domain"
    echo "3. Monitor logs: railway logs -f"
    echo "4. View metrics: railway open"
    echo ""
    echo -e "${GREEN}🎉 Backend deployment complete!${NC}"
}

# Main execution
main() {
    check_requirements
    prepare_deployment
    deploy_to_railway
    health_check
    show_next_steps
}

# Error handling
trap 'echo -e "\n${RED}❌ Deployment failed!${NC}\nCheck logs: railway logs" >&2' ERR

# Run deployment
main