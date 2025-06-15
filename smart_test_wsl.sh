#!/bin/bash
# Smart testing script 100% compatible with WSL/Linux

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧠 SMART TEST SUITE - IVA Margem Turismo (WSL Edition)${NC}"
echo "=================================================="

# Check dependencies first
echo -e "\n${YELLOW}Checking dependencies...${NC}"
MISSING_DEPS=0
for cmd in curl grep awk python3; do
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓ $cmd found${NC}"
    else
        echo -e "${RED}✗ $cmd not found${NC}"
        MISSING_DEPS=1
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${RED}Please install missing dependencies${NC}"
    exit 1
fi

# Function to check if port is open (WSL compatible)
check_port() {
    local port=$1
    # Try multiple methods to check port
    
    # Method 1: Try netcat if available
    if command -v nc &> /dev/null; then
        nc -z localhost $port 2>/dev/null
        return $?
    fi
    
    # Method 2: Try curl
    if curl -s --connect-timeout 1 http://localhost:$port > /dev/null 2>&1; then
        return 0
    fi
    
    # Method 3: Try telnet if available
    if command -v telnet &> /dev/null; then
        (echo quit | telnet localhost $port 2>/dev/null | grep -q Connected) && return 0
    fi
    
    # Method 4: Check with /proc/net/tcp (Linux specific)
    if [ -r /proc/net/tcp ]; then
        local hex_port=$(printf '%04X' $port)
        if grep -q ":$hex_port" /proc/net/tcp 2>/dev/null; then
            return 0
        fi
    fi
    
    return 1
}

# Function to test backend
test_backend() {
    echo -e "\n${BLUE}🔍 Backend Diagnostics${NC}"
    echo "====================="
    
    # Check if backend is running
    if check_port 8000; then
        echo -e "${GREEN}✓ Port 8000 is open${NC}"
        
        # Test root endpoint
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
        echo -e "${YELLOW}HTTP Response: $HTTP_CODE${NC}"
        
        if [ "$HTTP_CODE" = "200" ]; then
            echo -e "${GREEN}✓ Backend is healthy${NC}"
            return 0
        else
            echo -e "${RED}✗ Backend returned unexpected status${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Port 8000 is closed${NC}"
        echo -e "${YELLOW}Checking for uvicorn process...${NC}"
        
        # Check process without pgrep (more compatible)
        if ps aux | grep -v grep | grep -q "uvicorn app.main:app"; then
            echo -e "${YELLOW}Process is running but port not accessible${NC}"
            echo "Possible issues:"
            echo "- Process still starting up"
            echo "- Firewall blocking port"
            echo "- Binding to wrong interface"
        else
            echo -e "${RED}✗ Backend process not found${NC}"
            echo -e "\n${YELLOW}To start backend:${NC}"
            echo "cd backend && python3 -m uvicorn app.main:app --reload --host localhost"
        fi
        return 1
    fi
}

# Function to test data integrity
test_data_integrity() {
    echo -e "\n${BLUE}🔍 Data Integrity Test${NC}"
    echo "===================="
    
    # Get mock data
    RESPONSE=$(curl -s http://localhost:8000/api/mock-data 2>/dev/null)
    
    if [ -z "$RESPONSE" ]; then
        echo -e "${RED}✗ No response from API${NC}"
        return 1
    fi
    
    # Extract counts without jq (WSL compatible)
    SALES_COUNT=$(echo "$RESPONSE" | grep -o '"total_sales":[[:space:]]*[0-9]*' | grep -o '[0-9]*$')
    COSTS_COUNT=$(echo "$RESPONSE" | grep -o '"total_costs":[[:space:]]*[0-9]*' | grep -o '[0-9]*$')
    
    echo -e "${YELLOW}Sales found: $SALES_COUNT${NC}"
    echo -e "${YELLOW}Costs found: $COSTS_COUNT${NC}"
    
    # Verify exact counts
    if [ "$SALES_COUNT" = "26" ]; then
        echo -e "${GREEN}✓ Sales count correct (26)${NC}"
    else
        echo -e "${RED}✗ Sales count incorrect (expected 26, got $SALES_COUNT)${NC}"
    fi
    
    if [ "$COSTS_COUNT" = "157" ]; then
        echo -e "${GREEN}✓ Costs count correct (157)${NC}"
    else
        echo -e "${RED}✗ Costs count incorrect (expected 157, got $COSTS_COUNT)${NC}"
    fi
    
    # Check for specific cost entries
    if echo "$RESPONSE" | grep -q "TAP Portugal"; then
        echo -e "${GREEN}✓ Found TAP Portugal in costs${NC}"
    fi
    
    if echo "$RESPONSE" | grep -q "Booking.com"; then
        echo -e "${GREEN}✓ Found Booking.com in costs${NC}"
    fi
    
    # Extract session ID
    SESSION_ID=$(echo "$RESPONSE" | grep -o '"session_id":[[:space:]]*"[^"]*"' | cut -d'"' -f4)
    if [ -n "$SESSION_ID" ]; then
        echo -e "${GREEN}✓ Session ID generated: ${SESSION_ID:0:20}...${NC}"
    else
        echo -e "${RED}✗ No session ID found${NC}"
    fi
}

# Function to test frontend
test_frontend() {
    echo -e "\n${BLUE}🔍 Frontend Diagnostics${NC}"
    echo "====================="
    
    if check_port 8080; then
        echo -e "${GREEN}✓ Port 8080 is open${NC}"
        
        # Check if index.html exists
        if [ -f "frontend/index.html" ]; then
            echo -e "${GREEN}✓ index.html exists${NC}"
            
            # Test frontend accessibility
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/frontend/)
            if [ "$HTTP_CODE" = "200" ]; then
                echo -e "${GREEN}✓ Frontend accessible${NC}"
            else
                echo -e "${RED}✗ Frontend returned $HTTP_CODE${NC}"
            fi
        else
            echo -e "${RED}✗ index.html not found${NC}"
        fi
    else
        echo -e "${RED}✗ Port 8080 is closed${NC}"
        echo -e "\n${YELLOW}To start frontend:${NC}"
        echo "python3 -m http.server 8080"
    fi
}

# Main execution
main() {
    # Test backend
    if test_backend; then
        # If backend is running, test data
        test_data_integrity
    fi
    
    # Test frontend
    test_frontend
    
    # Summary and recommendations
    echo -e "\n${BLUE}📋 SUMMARY & RECOMMENDATIONS${NC}"
    echo "============================"
    
    if check_port 8000 && check_port 8080; then
        echo -e "${GREEN}✅ Both services are running!${NC}"
        echo -e "\n${YELLOW}Next steps:${NC}"
        echo "1. Open: http://localhost:8080/frontend/"
        echo "2. Press F12 → Console"
        echo "3. Run: localStorage.clear()"
        echo "4. Refresh page (F5)"
        echo "5. Click 'Usar Dados de Demonstração'"
        echo "6. Verify: 26 sales + 157 costs appear"
    else
        echo -e "${RED}⚠️  Some services are not running${NC}"
        echo -e "\n${YELLOW}Quick start command:${NC}"
        echo "./start_all_wsl.sh"
        echo -e "\n${YELLOW}Or manually:${NC}"
        echo "Terminal 1: cd backend && python3 -m uvicorn app.main:app --reload"
        echo "Terminal 2: python3 -m http.server 8080"
    fi
    
    # Performance tip
    echo -e "\n${BLUE}💡 PRO TIP:${NC}"
    echo "If data shows only 7 documents instead of 157:"
    echo "1. Clear browser cache completely"
    echo "2. Use incognito/private window"
    echo "3. Or run: localStorage.clear() in console"
}

# Run main
main