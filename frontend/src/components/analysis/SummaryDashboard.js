import React, { useState, useEffect } from 'react';

const SummaryDashboard = () => {
    // State hooks
    const [summaryData, setSummaryData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Effect hook to fetch data
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch('/api/summary'); // Replace with your API endpoint
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                const data = await response.json();
                setSummaryData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []); // Empty dependency array ensures this runs once on mount

    return (
        <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: {error}</p>}
            {!loading && !error && (
                <div>
                    {/* Render summaryData here */}
                    <pre>{JSON.stringify(summaryData, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default SummaryDashboard;