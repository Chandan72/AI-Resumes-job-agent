import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  RefreshCw, 
  Play, 
  Pause, 
  Clock, 
  TrendingUp, 
  Newspaper, 
  Settings,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  Loader
} from 'lucide-react';

const Dashboard = () => {
  const [industryStats, setIndustryStats] = useState([]);
  const [systemStats, setSystemStats] = useState({});
  const [schedulerStatus, setSchedulerStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [curationLoading, setCurationLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  // Industry categories
  const industries = [
    "Building Materials Sector",
    "Media & Entertainment",
    "Paper and Pulp Manufacturing",
    "Consumer Electronics",
    "Construction/Infrastructure",
    "Battery Manufacturing",
    "Mining and Minerals",
    "Ship Building",
    "Cement",
    "Pharmaceutical",
    "MSW Management",
    "NBFC",
    "Healthcare",
    "Aluminium",
    "Paint",
    "Telecommunications",
    "Oil and Gas",
    "Renewable Energy",
    "Explosives",
    "Financial Services",
    "Automobiles",
    "Textiles",
    "Travel and Tourism",
    "Auto Ancillaries",
    "Recruitment and Human Resources Services",
    "Power/Transmission & Equipment",
    "Real Estate & Construction Software",
    "Electronic Manufacturing Services",
    "Fast Moving Consumer Goods",
    "Contract Development and Manufacturing Organisation",
    "Fashion & Apparels",
    "Aviation"
  ];

  useEffect(() => {
    fetchData();
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch data in parallel
      const [statsResponse, systemResponse, schedulerResponse] = await Promise.all([
        axios.get('/industries'),
        axios.get('/stats'),
        axios.get('/scheduler/status')
      ]);

      setIndustryStats(statsResponse.data);
      setSystemStats(systemResponse.data);
      setSchedulerStatus(schedulerResponse.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const triggerCuration = async () => {
    try {
      setCurationLoading(true);
      await axios.post('/curate');
      
      // Wait a bit then refresh data
      setTimeout(() => {
        fetchData();
        setCurationLoading(false);
      }, 2000);
    } catch (err) {
      console.error('Error triggering curation:', err);
      setError('Failed to trigger news curation.');
      setCurationLoading(false);
    }
  };

  const toggleScheduler = async () => {
    try {
      if (schedulerStatus.is_running) {
        await axios.post('/scheduler/stop');
      } else {
        await axios.post('/scheduler/start');
      }
      fetchData();
    } catch (err) {
      console.error('Error toggling scheduler:', err);
      setError('Failed to toggle scheduler.');
    }
  };

  const getIndustryCard = (industryName) => {
    const stats = industryStats.find(s => s.industry === industryName);
    const articleCount = stats?.article_count || 0;
    const articles = stats?.articles || [];
    const avgConfidence = stats?.average_confidence || 0;

    return (
      <div key={industryName} className="industry-card">
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">
            {industryName}
          </h3>
          <div className="flex items-center space-x-2">
            <span className="status-indicator status-info">
              {articleCount} articles
            </span>
            {avgConfidence > 0 && (
              <span className="text-xs text-gray-500">
                {Math.round(avgConfidence * 100)}% conf.
              </span>
            )}
          </div>
        </div>

        {articles.length > 0 ? (
          <div className="space-y-2">
            {articles.slice(0, 5).map((article, idx) => (
              <div key={idx} className="text-xs">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="article-link block truncate"
                  title={article.title}
                >
                  {article.title}
                </a>
                <div className="flex items-center justify-between text-gray-500 mt-1">
                  <span className="text-xs">{article.source}</span>
                  <span className="text-xs">{article.published_date}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-400 text-xs italic">
            No articles available
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin h-8 w-8 text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Newspaper className="h-8 w-8 text-primary-600" />
              <h1 className="text-xl font-bold text-gray-900">
                AI News Curation Agent
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* System Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  schedulerStatus.is_running ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-sm text-gray-600">
                  {schedulerStatus.is_running ? 'Running' : 'Stopped'}
                </span>
              </div>

              {/* Last Updated */}
              {lastUpdated && (
                <div className="flex items-center space-x-1 text-sm text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>Updated: {lastUpdated.toLocaleTimeString()}</span>
                </div>
              )}

              {/* Refresh Button */}
              <button
                onClick={fetchData}
                className="btn-secondary flex items-center space-x-2"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Control Panel */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Control Panel</h2>
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleScheduler}
                className={`flex items-center space-x-2 ${
                  schedulerStatus.is_running ? 'btn-danger' : 'btn-primary'
                }`}
              >
                {schedulerStatus.is_running ? (
                  <>
                    <Pause className="h-4 w-4" />
                    <span>Stop Scheduler</span>
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    <span>Start Scheduler</span>
                  </>
                )}
              </button>

              <button
                onClick={triggerCuration}
                className="btn-primary flex items-center space-x-2"
                disabled={curationLoading}
              >
                {curationLoading ? (
                  <Loader className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                <span>
                  {curationLoading ? 'Running...' : 'Trigger Curation'}
                </span>
              </button>
            </div>
          </div>

          {/* System Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Newspaper className="h-5 w-5 text-blue-600" />
                <span className="text-sm font-medium text-gray-600">Total Articles (24h)</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {systemStats.total_articles_24h || 0}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                <span className="text-sm font-medium text-gray-600">Industries with Articles</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {systemStats.industries_with_articles || 0}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Clock className="h-5 w-5 text-purple-600" />
                <span className="text-sm font-medium text-gray-600">Next Execution</span>
              </div>
              <p className="text-sm font-medium text-gray-900">
                {schedulerStatus.next_execution ? 
                  new Date(schedulerStatus.next_execution).toLocaleString() : 
                  'Not scheduled'
                }
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-orange-600" />
                <span className="text-sm font-medium text-gray-600">Scheduler Status</span>
              </div>
              <span className={`status-indicator ${
                schedulerStatus.is_running ? 'status-success' : 'status-error'
              }`}>
                {schedulerStatus.is_running ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* Industry Grid */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">
              Industry News Dashboard
            </h2>
            <span className="text-sm text-gray-500">
              {industries.length} industries • Auto-refresh every 5 minutes
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {industries.map(industry => getIndustryCard(industry))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;