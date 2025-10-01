#!/bin/bash

# FabricStudio Controller - Workshop Schedule Backup/Restore Script
# API-based backup and restore for workshop_schedule.json

BACKUP_DIR="./backups"
API_URL="${API_URL:-http://localhost:8000}"
CONTAINER_NAME="${CONTAINER_NAME:-fabricchanger-fabricstudio-1}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to display usage
usage() {
    echo "Usage: $0 {backup|restore|list|latest} [options]"
    echo ""
    echo "Commands:"
    echo "  backup              Create a new backup of workshop schedule"
    echo "  restore <file>      Restore from a specific backup file"
    echo "  latest              Restore from the most recent backup"
    echo "  list                List all available backups"
    echo ""
    echo "Environment Variables:"
    echo "  API_URL             API endpoint (default: http://localhost:8000)"
    echo "  CONTAINER_NAME      Docker container name (default: fabricchanger-fabricstudio-1)"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 list"
    echo "  $0 restore backups/workshop_schedule_20250101_120000.json"
    echo "  $0 latest"
    echo "  API_URL=http://server:8000 $0 backup"
    exit 1
}

# Function to check if API is accessible
check_api() {
    if curl -s -f "${API_URL}/api/workshops" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to backup via API
backup_api() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/workshop_schedule_${timestamp}.json"
    
    echo -e "${BLUE}🔄 Connecting to API at ${API_URL}...${NC}"
    
    if ! check_api; then
        echo -e "${RED}❌ API not accessible at ${API_URL}${NC}"
        echo -e "${YELLOW}💡 Make sure the application is running${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📥 Downloading workshop schedule...${NC}"
    
    # Download the data via API
    local response=$(curl -s "${API_URL}/api/workshops")
    local success=$(echo "$response" | jq -r '.success')
    
    if [ "$success" != "true" ]; then
        echo -e "${RED}❌ API request failed${NC}"
        echo "$response" | jq '.'
        return 1
    fi
    
    # Extract and save the content
    echo "$response" | jq -r '.content' > "$backup_file"
    
    if [ $? -eq 0 ]; then
        local size=$(wc -c < "$backup_file" | tr -d ' ')
        local entries=$(jq 'length' "$backup_file" 2>/dev/null || echo "0")
        echo -e "${GREEN}✅ Backup created successfully!${NC}"
        echo -e "${GREEN}   File: $backup_file${NC}"
        echo -e "${GREEN}   Size: $size bytes${NC}"
        echo -e "${GREEN}   Entries: $entries workshops${NC}"
        
        # Clean up old backups (keep last 30)
        cleanup_old_backups
        return 0
    else
        echo -e "${RED}❌ Failed to save backup file${NC}"
        return 1
    fi
}

# Function to backup via docker cp (fallback)
backup_docker() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/workshop_schedule_${timestamp}.json"
    
    echo -e "${YELLOW}⚠️  API not accessible, trying Docker container...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        docker cp "${CONTAINER_NAME}:/app/workshop_schedule.json" "$backup_file" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            local size=$(wc -c < "$backup_file" | tr -d ' ')
            local entries=$(jq 'length' "$backup_file" 2>/dev/null || echo "0")
            echo -e "${GREEN}✅ Backup created from container!${NC}"
            echo -e "${GREEN}   File: $backup_file${NC}"
            echo -e "${GREEN}   Size: $size bytes${NC}"
            echo -e "${GREEN}   Entries: $entries workshops${NC}"
            
            cleanup_old_backups
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Backup failed: Container not accessible${NC}"
    return 1
}

# Function to restore via API
restore_api() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found: $backup_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔄 Connecting to API at ${API_URL}...${NC}"
    
    if ! check_api; then
        echo -e "${RED}❌ API not accessible at ${API_URL}${NC}"
        echo -e "${YELLOW}💡 Make sure the application is running${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📤 Restoring workshop schedule...${NC}"
    
    # Read backup file content
    local content=$(cat "$backup_file")
    local entries=$(echo "$content" | jq 'length' 2>/dev/null || echo "0")
    
    echo -e "${YELLOW}   Restoring $entries workshops...${NC}"
    
    # Prepare JSON payload
    local payload=$(jq -n --arg content "$content" '{content: $content}')
    
    # Send to API
    local response=$(curl -s -X POST "${API_URL}/api/workshops" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    local success=$(echo "$response" | jq -r '.success' 2>/dev/null)
    
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅ Restore completed successfully!${NC}"
        echo -e "${GREEN}   Source: $backup_file${NC}"
        echo -e "${GREEN}   Entries restored: $entries workshops${NC}"
        return 0
    else
        echo -e "${RED}❌ Restore failed${NC}"
        echo "$response" | jq '.'
        return 1
    fi
}

# Function to restore via docker cp (fallback)
restore_docker() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Backup file not found: $backup_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}⚠️  API not accessible, trying Docker container...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
        docker cp "$backup_file" "${CONTAINER_NAME}:/app/workshop_schedule.json" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            local entries=$(jq 'length' "$backup_file" 2>/dev/null || echo "0")
            echo -e "${GREEN}✅ Restore completed via container!${NC}"
            echo -e "${GREEN}   Source: $backup_file${NC}"
            echo -e "${GREEN}   Entries restored: $entries workshops${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}❌ Restore failed: Container not accessible${NC}"
    return 1
}

# Function to clean up old backups
cleanup_old_backups() {
    local keep=30
    local count=$(ls -1 "$BACKUP_DIR"/workshop_schedule_*.json 2>/dev/null | wc -l)
    
    if [ "$count" -gt "$keep" ]; then
        local to_delete=$((count - keep))
        ls -t "$BACKUP_DIR"/workshop_schedule_*.json | tail -n "+$((keep + 1))" | xargs rm 2>/dev/null
        echo -e "${BLUE}🧹 Cleaned up $to_delete old backup(s) (keeping last $keep)${NC}"
    fi
}

# Function to list backups
list_backups() {
    echo -e "${BLUE}📋 Available backups in ${BACKUP_DIR}:${NC}"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/workshop_schedule_*.json 2>/dev/null)" ]; then
        echo -e "${YELLOW}   No backups found${NC}"
        return 0
    fi
    
    printf "%-30s %-12s %-10s %s\n" "Backup File" "Size" "Entries" "Date"
    printf "%-30s %-12s %-10s %s\n" "----------------------------------------" "----------" "--------" "-------------------"
    
    ls -t "$BACKUP_DIR"/workshop_schedule_*.json 2>/dev/null | while read -r file; do
        local basename=$(basename "$file")
        local size=$(wc -c < "$file" | tr -d ' ')
        local size_kb=$((size / 1024))
        local entries=$(jq 'length' "$file" 2>/dev/null || echo "0")
        local date=$(echo "$basename" | sed 's/workshop_schedule_\([0-9]\{8\}\)_\([0-9]\{6\}\).json/\1 \2/' | awk '{print substr($1,1,4)"-"substr($1,5,2)"-"substr($1,7,2)" "substr($2,1,2)":"substr($2,3,2)":"substr($2,5,2)}')
        
        printf "%-30s %-12s %-10s %s\n" "$basename" "${size_kb}KB" "$entries" "$date"
    done
    
    echo ""
    local total=$(ls -1 "$BACKUP_DIR"/workshop_schedule_*.json 2>/dev/null | wc -l)
    echo -e "${GREEN}Total: $total backup(s)${NC}"
}

# Function to restore latest backup
restore_latest() {
    local latest=$(ls -t "$BACKUP_DIR"/workshop_schedule_*.json 2>/dev/null | head -n 1)
    
    if [ -z "$latest" ]; then
        echo -e "${RED}❌ No backups found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📦 Restoring from latest backup: $(basename "$latest")${NC}"
    restore "$latest"
}

# Main command handler
backup() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}   FabricStudio Workshop Backup${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    
    if backup_api; then
        return 0
    else
        backup_docker
        return $?
    fi
}

restore() {
    local backup_file="$1"
    
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}   FabricStudio Workshop Restore${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    
    if [ -z "$backup_file" ]; then
        echo -e "${RED}❌ Please specify a backup file${NC}"
        echo ""
        list_backups
        return 1
    fi
    
    # Confirm restore
    local entries=$(jq 'length' "$backup_file" 2>/dev/null || echo "0")
    echo -e "${YELLOW}⚠️  This will replace the current workshop schedule with $entries entries${NC}"
    echo -e "${YELLOW}   from: $(basename "$backup_file")${NC}"
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🚫 Restore cancelled${NC}"
        return 1
    fi
    
    if restore_api "$backup_file"; then
        return 0
    else
        restore_docker "$backup_file"
        return $?
    fi
}

# Check for required commands
for cmd in curl jq; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}❌ Required command not found: $cmd${NC}"
        echo -e "${YELLOW}💡 Please install $cmd to use this script${NC}"
        exit 1
    fi
done

# Parse command
case "$1" in
    backup)
        backup
        ;;
    restore)
        restore "$2"
        ;;
    latest)
        restore_latest
        ;;
    list)
        list_backups
        ;;
    *)
        usage
        ;;
esac

exit $?

