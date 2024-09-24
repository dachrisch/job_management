#!/usr/bin/env sh

# Check the value of WHICH_END
if [ "$WHICH_END" = "backend" ]; then
    # Run the backend-only command
    reflex run --env prod --backend-only
elif [ "$WHICH_END" = "frontend" ]; then
    # Run the frontend-only command
    reflex run --env prod --frontend-only
else
    # Error message for invalid values
    echo "Error: Invalid value for WHICH_END: $WHICH_END. Please set it to 'backend' or 'frontend'."
    exit 1
fi
