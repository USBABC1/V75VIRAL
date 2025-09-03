import { useState } from 'react';
import { TrendingUp, Zap, Target, Shield } from 'lucide-react';
import SearchForm from '@/react-app/components/SearchForm';
import SearchResults from '@/react-app/components/SearchResults';
import { SearchRequest, SearchResults as SearchResultsType } from '@/shared/types';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResultsType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (searchData: SearchRequest) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchData),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError('Failed to search for viral content. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24">
          <div className="text-center mb-16">
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className="p-3 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                ViralV1
              </h1>
            </div>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Discover trending content on Instagram and Facebook with powerful engagement analytics. 
              Find viral posts, analyze performance metrics, and stay ahead of social media trends.
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="text-center">
              <div className="p-4 bg-purple-100 rounded-2xl w-fit mx-auto mb-4">
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Lightning Fast</h3>
              <p className="text-slate-600">Get viral content results in seconds with our optimized search algorithms.</p>
            </div>
            <div className="text-center">
              <div className="p-4 bg-pink-100 rounded-2xl w-fit mx-auto mb-4">
                <Target className="h-8 w-8 text-pink-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Precise Analytics</h3>
              <p className="text-slate-600">Detailed engagement metrics including likes, comments, shares, and viral scores.</p>
            </div>
            <div className="text-center">
              <div className="p-4 bg-blue-100 rounded-2xl w-fit mx-auto mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Multi-Platform</h3>
              <p className="text-slate-600">Search across Instagram and Facebook to find trending content everywhere.</p>
            </div>
          </div>

          {/* Search Form */}
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />

          {/* Error Message */}
          {error && (
            <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-center">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-slate-800 mb-2">Search Results</h2>
            <p className="text-slate-600">
              Found {results.summary.total_images} viral images for "{results.search.query}"
            </p>
          </div>
          <SearchResults results={results} />
        </div>
      )}

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <TrendingUp className="h-6 w-6" />
            <span className="text-xl font-bold">ViralV1</span>
          </div>
          <p className="text-slate-400">
            Discover and analyze viral content across social media platforms
          </p>
        </div>
      </footer>
    </div>
  );
}
