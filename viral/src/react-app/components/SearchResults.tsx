import { useState } from 'react';
import { BarChart3, TrendingUp, Users, Filter, Grid, List } from 'lucide-react';
import { SearchResults as SearchResultsType } from '@/shared/types';
import ViralImageCard from './ViralImageCard';

interface SearchResultsProps {
  results: SearchResultsType;
}

export default function SearchResults({ results }: SearchResultsProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'engagement' | 'likes' | 'date'>('engagement');
  const [filterPlatform, setFilterPlatform] = useState<'all' | 'instagram' | 'facebook'>('all');

  const filteredAndSortedImages = results.images
    .filter(image => filterPlatform === 'all' || image.platform === filterPlatform)
    .sort((a, b) => {
      switch (sortBy) {
        case 'engagement':
          return b.engagement_score - a.engagement_score;
        case 'likes':
          return b.likes_estimate - a.likes_estimate;
        case 'date':
          return new Date(b.post_date).getTime() - new Date(a.post_date).getTime();
        default:
          return 0;
      }
    });

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-800">
                {results.summary.total_images}
              </div>
              <div className="text-sm text-slate-600">Viral Images</div>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-800">
                {results.summary.avg_engagement.toFixed(1)}
              </div>
              <div className="text-sm text-slate-600">Avg Engagement</div>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-800">
                {results.summary.top_authors.length}
              </div>
              <div className="text-sm text-slate-600">Top Creators</div>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Filter className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-800">
                {Object.keys(results.summary.platform_distribution).length}
              </div>
              <div className="text-sm text-slate-600">Platforms</div>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Distribution */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 shadow-lg">
        <h3 className="text-lg font-semibold text-slate-800 mb-4">Platform Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(results.summary.platform_distribution).map(([platform, count]) => (
            <div key={platform} className="text-center">
              <div className={`inline-block px-4 py-2 rounded-lg text-white font-semibold ${
                platform === 'instagram' 
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500' 
                  : 'bg-blue-600'
              }`}>
                {count}
              </div>
              <div className="text-sm text-slate-600 mt-1 capitalize">{platform}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-wrap gap-4">
          {/* Sort Controls */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'engagement' | 'likes' | 'date')}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none bg-white"
          >
            <option value="engagement">Sort by Engagement</option>
            <option value="likes">Sort by Likes</option>
            <option value="date">Sort by Date</option>
          </select>

          {/* Platform Filter */}
          <select
            value={filterPlatform}
            onChange={(e) => setFilterPlatform(e.target.value as 'all' | 'instagram' | 'facebook')}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:border-purple-500 focus:outline-none bg-white"
          >
            <option value="all">All Platforms</option>
            <option value="instagram">Instagram Only</option>
            <option value="facebook">Facebook Only</option>
          </select>
        </div>

        {/* View Mode Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'grid'
                ? 'bg-purple-100 text-purple-600'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Grid className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-lg transition-colors ${
              viewMode === 'list'
                ? 'bg-purple-100 text-purple-600'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Results */}
      {filteredAndSortedImages.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-slate-400 text-lg">No images match your current filters</div>
        </div>
      ) : (
        <div className={`grid gap-6 ${
          viewMode === 'grid' 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' 
            : 'grid-cols-1'
        }`}>
          {filteredAndSortedImages.map((image, index) => (
            <ViralImageCard key={index} image={image} />
          ))}
        </div>
      )}
    </div>
  );
}
