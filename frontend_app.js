import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { throttle } from 'lodash-es';

const App = () => {
    const [stats, setStats] = useState({});
    const [anomalies, setAnomalies] = useState([]);
    
    const fetchData = useMemo(() => throttle(async () => {
        try {
            const [statsRes, anomaliesRes] = await Promise.all([
                fetch('/api/network/stats'),
                fetch('/api/anomalies')
            ]);
            
            setStats(await statsRes.json());
            setAnomalies(await anomaliesRes.json());
        } catch (error) {
            console.error('Data fetch error:', error);
        }
    }, 1000), []);

    useEffect(() => {
        const interval = setInterval(fetchData, 1000);
        return () => clearInterval(interval);
    }, [fetchData]);

    return (
        <div className="dashboard">
            <RealTimeNetworkGraph data={stats} />
            <AnomalyTable data={anomalies} />
            <SystemHealthMonitor />
        </div>
    );
};

const root = createRoot(document.getElementById('root'));
root.render(<App />);
