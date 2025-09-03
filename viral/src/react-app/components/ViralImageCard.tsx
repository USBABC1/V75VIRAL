import { ExternalLink, Heart, MessageCircle, Share, Eye, User, Calendar, Hash } from 'lucide-react';
import { ViralImage } from '@/shared/types';

interface ViralImageCardProps {
  image: ViralImage;
}

export default function ViralImageCard({ image }: ViralImageCardProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'instagram':
        return 'bg-gradient-to-r from-purple-500 to-pink-500';
      case 'facebook':
        return 'bg-blue-600';
      default:
        return 'bg-gray-600';
    }
  };

  const getEngagementColor = (score: number) => {
    if (score >= 75) return 'text-green-600 bg-green-100';
    if (score >= 50) return 'text-yellow-600 bg-yellow-100';
    if (score >= 25) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden border border-slate-200 hover:border-purple-200 group">
      {/* Image Section */}
      <div className="relative overflow-hidden">
        <img
          src={image.image_url}
          alt={image.title}
          className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=256&fit=crop&crop=center';
          }}
        />
        
        {/* Platform Badge */}
        <div className={`absolute top-4 left-4 px-3 py-1 rounded-full text-white text-sm font-semibold ${getPlatformColor(image.platform)}`}>
          {image.platform.charAt(0).toUpperCase() + image.platform.slice(1)}
        </div>

        {/* Engagement Score */}
        <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-sm font-bold ${getEngagementColor(image.engagement_score)}`}>
          {image.engagement_score}
        </div>
      </div>

      {/* Content Section */}
      <div className="p-6 space-y-4">
        {/* Title and Description */}
        <div>
          <h3 className="font-bold text-lg text-slate-800 line-clamp-2 mb-2">
            {image.title || 'Viral Content'}
          </h3>
          {image.description && (
            <p className="text-slate-600 text-sm line-clamp-3">
              {image.description}
            </p>
          )}
        </div>

        {/* Author Info */}
        {image.author && (
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <User className="h-4 w-4" />
            <span className="font-medium">@{image.author}</span>
            {image.author_followers > 0 && (
              <span className="text-slate-400">
                • {formatNumber(image.author_followers)} followers
              </span>
            )}
          </div>
        )}

        {/* Engagement Metrics */}
        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <Heart className="h-4 w-4 text-red-500" />
            <span>{formatNumber(image.likes_estimate)}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-600">
            <MessageCircle className="h-4 w-4 text-blue-500" />
            <span>{formatNumber(image.comments_estimate)}</span>
          </div>
          {image.shares_estimate > 0 && (
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Share className="h-4 w-4 text-green-500" />
              <span>{formatNumber(image.shares_estimate)}</span>
            </div>
          )}
          {image.views_estimate > 0 && (
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <Eye className="h-4 w-4 text-purple-500" />
              <span>{formatNumber(image.views_estimate)}</span>
            </div>
          )}
        </div>

        {/* Hashtags */}
        {image.hashtags && image.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {image.hashtags.slice(0, 3).map((tag, index) => (
              <div key={index} className="flex items-center gap-1 px-2 py-1 bg-slate-100 rounded-lg text-xs text-slate-600">
                <Hash className="h-3 w-3" />
                {tag}
              </div>
            ))}
            {image.hashtags.length > 3 && (
              <div className="px-2 py-1 bg-slate-100 rounded-lg text-xs text-slate-600">
                +{image.hashtags.length - 3} more
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-200">
          {image.post_date && (
            <div className="flex items-center gap-1 text-xs text-slate-500">
              <Calendar className="h-3 w-3" />
              {formatDate(image.post_date)}
            </div>
          )}
          
          <a
            href={image.post_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 px-3 py-1 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm text-slate-700 transition-colors"
          >
            <ExternalLink className="h-3 w-3" />
            View Post
          </a>
        </div>
      </div>
    </div>
  );
}
