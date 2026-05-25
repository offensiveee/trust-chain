#!/bin/bash
# TrustedChain Server Management Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "$1" in
    start)
        echo "Starting TrustedChain server..."
        python3 server.py &
        echo $! > server.pid
        echo "Server started with PID: $(cat server.pid)"
        echo "Access at: http://localhost:4173/"
        ;;
    stop)
        if [ -f server.pid ]; then
            PID=$(cat server.pid)
            kill $PID 2>/dev/null && echo "Server stopped (PID: $PID)" || echo "Server not running"
            rm -f server.pid
        else
            echo "No PID file found. Killing all server.py processes..."
            pkill -f "python3 server.py"
        fi
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    status)
        if [ -f server.pid ]; then
            PID=$(cat server.pid)
            if ps -p $PID > /dev/null 2>&1; then
                echo "Server running (PID: $PID)"
            else
                echo "PID file exists but process not running"
                rm -f server.pid
            fi
        else
            if pgrep -f "python3 server.py" > /dev/null; then
                echo "Server running but no PID file"
            else
                echo "Server not running"
            fi
        fi
        ;;
    logs)
        tail -f trustchain.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check server status"
        echo "  logs    - View server logs (live)"
        exit 1
        ;;
esac
