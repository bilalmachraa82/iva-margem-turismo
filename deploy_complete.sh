#!/bin/bash
# Complete Deployment Script - Backend + Frontend + Database
# One command to deploy everything

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 IVA MARGEM TURISMO - COMPLETE DEPLOYMENT${NC}"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please copy .env.example to .env and fill in your values:"
    echo "cp .env.example .env"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required variables
required_vars=("DATABASE_URL" "VERCEL_TOKEN" "RAILWAY_TOKEN" "NEON_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Missing required variable: $var${NC}"
        echo "Please set it in your .env file"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment loaded${NC}"
echo ""

# Step 1: Database Migration
echo -e "${BLUE}═══ STEP 1/4: Database Setup ═══${NC}"
echo ""
cd backend
if [ ! -f "database.py" ]; then
    echo -e "${YELLOW}Running database migration...${NC}"
    python3 migrate_to_postgres.py
else
    echo -e "${GREEN}✅ Database already migrated${NC}"
fi
cd ..

# Step 2: Backend Deployment
echo -e "\n${BLUE}═══ STEP 2/4: Backend Deployment ═══${NC}"
echo ""
chmod +x deploy_backend.sh
./deploy_backend.sh "$RAILWAY_TOKEN"

# Get backend URL from Railway
echo -e "\n${YELLOW}Getting backend URL...${NC}"
BACKEND_URL=$(cd backend && railway status | grep -oP 'https://[^\s]+' | head -1)
if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠️  Could not auto-detect backend URL${NC}"
    echo "Please enter your Railway backend URL:"
    read -r BACKEND_URL
fi
export BACKEND_URL

# Step 3: Frontend Deployment
echo -e "\n${BLUE}═══ STEP 3/4: Frontend Deployment ═══${NC}"
echo ""
chmod +x deploy_frontend.sh
./deploy_frontend.sh "$VERCEL_TOKEN" "$BACKEND_URL"

# Step 4: Final Validation
echo -e "\n${BLUE}═══ STEP 4/4: Validation ═══${NC}"
echo ""

# Test backend
echo -e "${YELLOW}Testing backend...${NC}"
if curl -s -f "$BACKEND_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Summary
echo -e "\n${PURPLE}════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${PURPLE}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "Backend API: ${YELLOW}$BACKEND_URL${NC}"
echo -e "API Docs: ${YELLOW}$BACKEND_URL/docs${NC}"
echo -e "Frontend: ${YELLOW}https://iva-margem-turismo.vercel.app${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Test the application thoroughly"
echo "2. Configure custom domain (optional)"
echo "3. Set up monitoring alerts"
echo "4. Create backup schedule"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"