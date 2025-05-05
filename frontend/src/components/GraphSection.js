import React, { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    BarChart,
    Bar,
} from 'recharts';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const GraphSection = ({ companyId }) => {
    const [loading, setLoading] = useState(true);
    const [timeFrame, setTimeFrame] = useState('all');
    const [stockData, setStockData] = useState(null);
    const [financialData, setFinancialData] = useState(null);
    const [chartType, setChartType] = useState('line');

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            console.log(`[DEBUG] fetchData: Fetching data for companyId: ${companyId}, timeFrame: ${timeFrame}`); // Debug
            try {
                // Fetch stock data
                const stockResponse = await fetch(`/api/company/${companyId}/stock_data?timeframe=${timeFrame}`);
                console.log(`[DEBUG] fetchData: Stock data response status: ${stockResponse.status}`); // Debug
                if (!stockResponse.ok) {
                    const errorText = await stockResponse.text(); // Get the error message
                    console.error(`[ERROR] fetchData: Failed to fetch stock data.  Status: ${stockResponse.status},  Response Text: ${errorText}`);
                    throw new Error(`Failed to fetch stock data: ${stockResponse.status} - ${errorText}`);
                }
                const stockJson = await stockResponse.json();
                console.log('[DEBUG] fetchData: Stock data:`, stockJson');
                setStockData(stockJson.stock_data);

                // Fetch financial data
                const financialResponse = await fetch(`/api/company/${companyId}/financial_data`);
                console.log(`[DEBUG] fetchData: Financial data response status: ${financialResponse.status}`); // Debug
                if (!financialResponse.ok) {
                    const errorText = await financialResponse.text();
                    console.error(`[ERROR] fetchData: Failed to fetch financial data. Status: ${financialResponse.status}, Response Text: ${errorText}`);
                    throw new Error(`Failed to fetch financial data: ${financialResponse.status} - ${errorText}`);
                }
                const financialJson = await financialResponse.json();
                console.log('[DEBUG] fetchData: Financial data:`, financialJson');
                setFinancialData(financialJson.financial_data && financialJson.financial_data.length > 0 ? financialJson.financial_data[0] : null);

            } catch (error) {
                console.error("Error fetching data:", error);
                // Handle error (e.g., show error message to user)
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [companyId, timeFrame]);

    const getFilteredStockData = () => {
        if (!stockData) {
            console.log('[DEBUG] getFilteredStockData: stockData is null or undefined, returning empty array');
            return [];
        }

        let data = [...stockData];
        console.log(`[DEBUG] getFilteredStockData: Initial data length: ${data.length}, timeFrame: ${timeFrame}`); // Debug
        switch (timeFrame) {
            case '1w':
                data = data.slice(Math.max(0, data.length - 7));
                break;
            case '1m':
                data = data.slice(Math.max(0, data.length - 30));
                break;
            case '1y':
                data = data.slice(Math.max(0, data.length - 365));
                break;
            case '5y':
                data = data.slice(Math.max(0, data.length - 365 * 5));
                break;
            case 'all':
            default:
                break;
        }
        console.log('[DEBUG] getFilteredStockData: Filtered data length:', data.length); // Debug
        return data;
    };

    const filteredStockData = getFilteredStockData();

    const formatYAxis = (value) => value.toFixed(2);

    const renderStockPriceChart = () => {
        if (loading) {
            return <Skeleton className="w-full h-[300px]" />;
        }
        if (!stockData || stockData.length === 0) {
            return <p className="text-gray-500 text-center">No stock data available.</p>;
        }

        const ChartComponent = chartType === 'line' ? LineChart : BarChart;
        const LineOrBar = chartType === 'line' ? Line : Bar;

        return (
            <ResponsiveContainer width="100%" height={300}>
                <ChartComponent
                    data={filteredStockData}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis tickFormatter={formatYAxis} />
                    <Tooltip />
                    <Legend />
                    <LineOrBar
                        type="monotone"
                        dataKey="close"
                        stroke={chartType === 'line' ? "#8884d8" : "#8884d8"}
                        fill={chartType === 'bar' ? "#8884d8" : undefined}
                        activeDot={chartType === 'line' ? { r: 8 } : undefined}
                        name="Price"
                    />
                </ChartComponent>
            </ResponsiveContainer>
        );
    };

    const renderVolumeChart = () => {
        if (loading) {
            return <Skeleton className="w-full h-[300px]" />;
        }
        if (!stockData || stockData.length === 0) {
            return <p className="text-gray-500 text-center">No stock data available.</p>;
        }
        const ChartComponent = chartType === 'line' ? LineChart : BarChart;
        const LineOrBar = chartType === 'line' ? Line : Bar;

        return (
            <ResponsiveContainer width="100%" height={300}>
                <ChartComponent
                    data={filteredStockData}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <LineOrBar
                        type="monotone"
                        dataKey="volume"
                        stroke={chartType === 'line' ? "#82ca9d" : "#82ca9d"}
                        fill={chartType === 'bar' ? "#82ca9d" : undefined}
                        activeDot={chartType === 'line' ? { r: 8 } : undefined}
                        name="Volume"
                    />
                </ChartComponent>
            </ResponsiveContainer>
        );
    };

    const renderFinancialData = () => {
        if (loading) {
            return (
                <div className="grid grid-cols-2 gap-4">
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                    <Skeleton className="h-6 w-full" />
                </div>
            );
        }
        if (!financialData) {
            return <p className="text-gray-500">No financial data available.</p>;
        }

        return (
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <span className="font-semibold">Date:</span> {financialData.date}
                </div>
                <div>
                    <span className="font-semibold">Open:</span> {financialData.open !== null && financialData.open !== undefined ? financialData.open.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">High:</span> {financialData.high !== null && financialData.high !== undefined ? financialData.high.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Low:</span> {financialData.low !== null && financialData.low !== undefined ? financialData.low.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Close:</span> {financialData.close !== null && financialData.close !== undefined ? financialData.close.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Volume:</span> {financialData.volume !== null && financialData.volume !== undefined ? financialData.volume.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">ROI:</span> {financialData.roi !== null && financialData.roi !== undefined ? financialData.roi.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">EPS:</span> {financialData.eps !== null && financialData.eps !== undefined ? financialData.eps.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">PE Ratio:</span> {financialData.pe_ratio !== null && financialData.pe_ratio !== undefined ? financialData.pe_ratio.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Revenue:</span>  {financialData.revenue !== null && financialData.revenue !== undefined ? financialData.revenue.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Debt to Equity:</span>  {financialData.debt_to_equity !== null && financialData.debt_to_equity !== undefined ? financialData.debt_to_equity.toFixed(2) : 'N/A'}
                </div>
                <div>
                    <span className="font-semibold">Cash Flow:</span>  {financialData.cash_flow !== null && financialData.cash_flow !== undefined ? financialData.cash_flow.toFixed(2) : 'N/A'}
                </div>
                {/* Add other financial metrics as needed */}
            </div>
        );
    };

    return (
        <Card className="graph-financial-info">
            <CardContent>
                <h3 className="section-title">Graphs and Key Financial Information</h3>
                <div className="row">
                    <div className="col-md-6">
                        <div className="flex items-center justify-between mb-2">
                            <h4>Stock Price Trend</h4>
                            <div className="flex items-center gap-2">
                                <Select onValueChange={setTimeFrame} value={timeFrame}>
                                    <SelectTrigger className="w-[180px]">
                                        <SelectValue placeholder="Select Time Frame" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="1w">Last 7 Days</SelectItem>
                                        <SelectItem value="1m">Last 30 Days</SelectItem>
                                        <SelectItem value="1y">Last Year</SelectItem>
                                        <SelectItem value="5y">Last 5 Years</SelectItem>
                                        <SelectItem value="all">All Time</SelectItem>
                                    </SelectContent>
                                </Select>
                                <Select onValueChange={setChartType} value={chartType}>
                                    <SelectTrigger className="w-[130px]">
                                        <SelectValue placeholder="Chart Type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="line">Line Chart</SelectItem>
                                        <SelectItem value="bar">Bar Chart</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="graph-container">
                            {renderStockPriceChart()}
                        </div>
                    </div>
                    <div className="col-md-6">
                        <h4>Volume Trend</h4>
                        <div className="graph-container">
                            {renderVolumeChart()}
                        </div>
                    </div>
                </div>
                <h4 className="mt-3">Key Financial Data</h4>
                {renderFinancialData()}
            </CardContent>
        </Card>
    );
};

export default GraphSection;