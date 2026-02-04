const getWebSocketUrl = () => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    // Remove /api and replace protocol
    const baseUrl = apiUrl.replace('/api', '').replace(/^http/, 'ws');
    return `${baseUrl}/ws`;
};

class LiveUpdateService {
    constructor() {
        this.ws = null;
        this.callbacks = [];
        this.currentYear = 2050;
    }

    connect() {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            return;
        }

        this.ws = new WebSocket(getWebSocketUrl());

        this.ws.onopen = () => {
            console.log('Connected to live updates');
            // Send initial year
            this.setYear(this.currentYear);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.notify(data);
            } catch (e) {
                console.error('Error parsing live update:', e);
            }
        };

        this.ws.onclose = () => {
            console.log('Live updates disconnected, retrying in 5s...');
            setTimeout(() => this.connect(), 5000);
        };

        this.ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            // On error, we might want to close to trigger reconnect logic
            // but often onclose is called anyway.
        };
    }

    setYear(year) {
        this.currentYear = year;
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ year }));
        }
    }

    subscribe(callback) {
        this.callbacks.push(callback);
        return () => {
            this.callbacks = this.callbacks.filter(cb => cb !== callback);
        };
    }

    notify(data) {
        this.callbacks.forEach(cb => cb(data));
    }
}

export const liveUpdateService = new LiveUpdateService();
