import { useState } from 'react';
import { Search, Settings, Loader2 } from 'lucide-react';
import { SearchRequest } from '@/shared/types';

interface SearchFormProps {
  onSearch: (searchData: SearchRequest) => void;
  isLoading: boolean;
}

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxImages, setMaxImages] = useState(20);
  const [minEngagement, setMinEngagement] = useState(0);
  const [platforms, setPlatforms] = useState<('instagram' | 'facebook')[]>(['instagram', 'facebook']);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    onSearch({
      query: query.trim(),
      max_images: maxImages,
      min_engagement: minEngagement,
      platforms
    });
  };

  const togglePlatform = (platform: 'instagram' | 'facebook') => {
    setPlatforms(prev => 
      prev.includes(platform) 
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Search Input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
            <Search className="h-6 w-6 text-slate-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for viral content... (e.g., 'marketing digital', 'curso gratis')"
            className="w-full pl-16 pr-6 py-4 text-lg border-2 border-slate-200 rounded-2xl focus:border-purple-500 focus:outline-none transition-colors bg-white/80 backdrop-blur-sm shadow-lg"
            disabled={isLoading}
          />
        </div>

        {/* Advanced Settings */}
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-slate-600 hover:text-slate-800 transition-colors"
            disabled={isLoading}
          >
            <Settings className="h-4 w-4" />
            Advanced Settings
          </button>

          <button
            type="submit"
            disabled={!query.trim() || isLoading || platforms.length === 0}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Searching...
              </div>
            ) : (
              'Find Viral Content'
            )}
          </button>
        </div>

        {/* Advanced Settings Panel */}
        {showAdvanced && (
          <div className="p-6 bg-white/60 backdrop-blur-sm rounded-2xl border border-slate-200 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Max Images */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Max Results
                </label>
                <select
                  value={maxImages}
                  onChange={(e) => setMaxImages(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none"
                  disabled={isLoading}
                >
                  <option value={10}>10 results</option>
                  <option value={20}>20 results</option>
                  <option value={30}>30 results</option>
                  <option value={50}>50 results</option>
                </select>
              </div>

              {/* Min Engagement */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Min Engagement Score
                </label>
                <select
                  value={minEngagement}
                  onChange={(e) => setMinEngagement(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none"
                  disabled={isLoading}
                >
                  <option value={0}>Any engagement</option>
                  <option value={10}>10+ score</option>
                  <option value={25}>25+ score</option>
                  <option value={50}>50+ score</option>
                  <option value={75}>75+ score</option>
                </select>
              </div>

              {/* Platforms */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Platforms
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => togglePlatform('instagram')}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      platforms.includes('instagram')
                        ? 'bg-purple-100 border-purple-300 text-purple-700'
                        : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
                    }`}
                    disabled={isLoading}
                  >
                    Instagram
                  </button>
                  <button
                    type="button"
                    onClick={() => togglePlatform('facebook')}
                    className={`px-4 py-2 rounded-lg border transition-colors ${
                      platforms.includes('facebook')
                        ? 'bg-blue-100 border-blue-300 text-blue-700'
                        : 'bg-white border-slate-300 text-slate-600 hover:bg-slate-50'
                    }`}
                    disabled={isLoading}
                  >
                    Facebook
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
