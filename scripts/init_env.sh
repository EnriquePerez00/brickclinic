#!/bin/bash

# Platform Engineer Setup
# Automates checks for Docker and Supabase before starting dev server

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🛠️  [Platform Check] Verifying Environment..."

# 1. Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is NOT running.${NC}"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

# 2. Check Supabase Status (Fast Check)
# Instead of slow 'supabase status', we check if the API Gateway port (54321) is open
if [ -f "supabase/config.toml" ]; then
    # Check if port 54321 is listening (simulates "Is Supabase Running?")
    # nc -z checks for open port without sending data
    if nc -z 127.0.0.1 54321 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Database Environment Ready (Port 54321 Active)${NC}"
    else
        echo -e "${YELLOW}⚠️  Supabase appears stopped (Port 54321 closed). Starting services...${NC}"
        npx supabase start > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database Environment Ready (Supabase Started)${NC}"
        else
            echo -e "${RED}❌ Failed to start Supabase.${NC}"
            # Don't exit 1 here, maybe they want to run dev anyway
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Skipping Supabase check (no config found).${NC}"
fi
