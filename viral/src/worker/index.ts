import { Hono } from "hono";
import { cors } from "hono/cors";
import { zValidator } from "@hono/zod-validator";
import { SearchRequestSchema } from "../shared/types";
import { serve } from '@hono/node-server';

// NOTE: This worker is designed to run in a Node.js environment.
// It uses Node.js APIs for file system access (`fs/promises`).
// This will not run in a standard Cloudflare Worker environment without modification.
import fs from 'fs/promises';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// --- Local Database Setup ---
const DB_FILE = path.join(__dirname, 'local_viral_db.json');

interface ViralImage {
  search_id: string;
  image_url: string;
  post_url: string;
  platform: string;
  title: string;
  description: string;
  engagement_score: number;
  views_estimate: number;
  likes_estimate: number;
  comments_estimate: number;
  shares_estimate: number;
  author: string;
  author_followers: number;
  post_date: string;
  hashtags: string[];
}

interface SearchRecord {
  id: string;
  query: string;
  status: 'processing' | 'completed' | 'failed';
  total_results: number;
  created_at: string;
  completed_at?: string;
  images: ViralImage[];
}

interface LocalDatabase {
  searches: SearchRecord[];
}

async function readDb(): Promise<LocalDatabase> {
  try {
    await fs.access(DB_FILE);
    const data = await fs.readFile(DB_FILE, 'utf-8');
    return JSON.parse(data) as LocalDatabase;
  } catch (error) {
    // If the file doesn't exist, return a default structure
    return { searches: [] };
  }
}

async function writeDb(data: LocalDatabase): Promise<void> {
  await fs.writeFile(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
}


// --- Hono App ---

interface Env {
  // We no longer use D1, but keep the bindings for other keys
  DB?: any; // Optional D1 binding
  SERPER_API_KEY: string;
  APIFY_API_KEY: string;
  OPENROUTER_API_KEY: string;
  FIRECRAWL_API_KEY: string;
  INSTAGRAM_SESSION_COOKIE: string;
}

const app = new Hono<{ Bindings: Env }>();

app.use("*", cors());

// Real viral image search endpoint
app.post("/api/search", zValidator("json", SearchRequestSchema), async (c) => {
  const { query, max_images, min_engagement, platforms } = c.req.valid("json");
  const searchId = uuidv4();

  const newSearch: SearchRecord = {
    id: searchId,
    query,
    status: 'processing',
    total_results: 0,
    created_at: new Date().toISOString(),
    images: []
  };

  try {
    console.log(`Starting viral search for query: "${query}" with platforms: ${platforms.join(', ')}`);

    const viralImages = await findRealViralImages(c.env, {
      query,
      max_images,
      min_engagement,
      platforms,
      searchId
    });

    newSearch.images = viralImages;
    newSearch.status = 'completed';
    newSearch.total_results = viralImages.length;
    newSearch.completed_at = new Date().toISOString();

    const db = await readDb();
    db.searches.unshift(newSearch); // Add to the beginning of the list
    await writeDb(db);

    const summary = calculateRealSummary(viralImages);

    return c.json({
      search: { ...newSearch, images: undefined }, // Don't return all images in the search object
      images: viralImages,
      summary
    });

  } catch (error) {
    console.error("Search error:", error);
    newSearch.status = 'failed';
    newSearch.completed_at = new Date().toISOString();
    
    try {
        const db = await readDb();
        db.searches.unshift(newSearch);
        await writeDb(db);
    } catch (dbError) {
        console.error('Failed to write failed search status to local db:', dbError);
    }

    return c.json({ 
      error: "Failed to find viral content", 
      details: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
    }, 500);
  }
});

// Get search history
app.get("/api/searches", async (c) => {
  const db = await readDb();
  // Return search records without the images array for performance
  const searchHistory = db.searches.map(s => ({...s, images: undefined}));
  return c.json(searchHistory);
});

// Get search results by ID
app.get("/api/search/:id", async (c) => {
  const searchId = c.req.param("id");
  const db = await readDb();

  const search = db.searches.find(s => s.id === searchId);

  if (!search) {
    return c.json({ error: "Search not found" }, 404);
  }

  const summary = calculateRealSummary(search.images);

  return c.json({
    search: {...search, images: undefined},
    images: search.images,
    summary
  });
});

// Real viral image finder using multiple APIs
async function findRealViralImages(env: Env, options: {
  query: string;
  max_images: number;
  min_engagement: number;
  platforms: string[];
  searchId: string;
}): Promise<ViralImage[]> {
  const { query, max_images, min_engagement, platforms, searchId } = options;
  console.log(`Finding real viral images for: ${query}`);

  const allViralImages: ViralImage[] = [];
  
  for (const platform of platforms) {
    try {
      console.log(`Searching ${platform} for viral content...`);

      let platformImages = [];
      
      if (platform === 'instagram') {
        platformImages = await scrapeInstagramViral(env, query, Math.ceil(max_images / platforms.length));
      } else if (platform === 'facebook') {
        platformImages = await scrapeFacebookViral(env, query, Math.ceil(max_images / platforms.length));
      }

      console.log(`Found ${platformImages.length} potential viral images on ${platform}`);

      for (const image of platformImages) {
        try {
          const analysisResult = await analyzeRealEngagement(env, image, platform);

          if (analysisResult && analysisResult.engagement_score >= min_engagement) {
            const viralImage: ViralImage = {
              search_id: searchId,
              image_url: analysisResult.image_url || image.image_url,
              post_url: analysisResult.post_url || image.post_url,
              platform,
              title: analysisResult.title || image.title || 'Viral Content',
              description: analysisResult.description || image.description || '',
              engagement_score: analysisResult.engagement_score,
              views_estimate: analysisResult.views_estimate || 0,
              likes_estimate: analysisResult.likes_estimate || 0,
              comments_estimate: analysisResult.comments_estimate || 0,
              shares_estimate: analysisResult.shares_estimate || 0,
              author: analysisResult.author || 'Unknown',
              author_followers: analysisResult.author_followers || 0,
              post_date: analysisResult.post_date || new Date().toISOString(),
              hashtags: analysisResult.hashtags || []
            };

            allViralImages.push(viralImage);
            console.log(`Successfully processed and added ${platform} post: ${image.id}`);
          } else {
            console.log(`Skipping ${platform} post ${image.id}: low engagement`);
          }
        } catch (error) {
          console.error(`Failed to analyze image ${image.id}:`, error);
        }
      }
    } catch (error) {
      console.error(`Failed to search ${platform}:`, error);
    }
  }

  return allViralImages
    .sort((a, b) => b.engagement_score - a.engagement_score)
    .slice(0, max_images);
}

// The rest of the scraper/analyzer functions remain the same as they don't interact with the DB
// scrapeInstagramViral, scrapeFacebookViral, searchInstagramWithSerper,
// analyzeRealEngagement, extractRealMetrics, analyzeWithOpenRouter,
// calculateEngagementScore, calculateRealSummary

// Instagram viral content scraper using Apify
async function scrapeInstagramViral(env: Env, query: string, maxResults: number) {
  console.log(`Scraping Instagram for: ${query}`);
  
  try {
    const runInput = {
      hashtags: [query.replace(/\s+/g, '')],
      resultsLimit: maxResults,
      addParentData: false
    };

    const response = await fetch(`https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items?token=${env.APIFY_API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(runInput),
    });

    if (!response.ok) {
      throw new Error(`Apify Instagram scraper failed: ${response.status}`);
    }

    const data = await response.json() as any[];
    console.log(`Apify returned ${data.length} Instagram results`);

    return data.map((item: any) => ({
      id: item.id || item.shortCode,
      image_url: item.displayUrl || item.thumbnail,
      post_url: `https://instagram.com/p/${item.shortCode}`,
      title: item.caption ? item.caption.substring(0, 100) : '',
      description: item.caption || '',
      raw_data: item
    }));

  } catch (error) {
    console.error('Instagram scraping failed:', error);
    return await searchInstagramWithSerper(env, query, maxResults);
  }
}

// Facebook viral content scraper using Apify
async function scrapeFacebookViral(env: Env, query: string, maxResults: number) {
  console.log(`Scraping Facebook for: ${query}`);
  
  try {
    const response = await fetch("https://google.serper.dev/search", {
      method: "POST",
      headers: {
        "X-API-KEY": env.SERPER_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: `site:facebook.com "${query}" viral popular engagement`,
        num: maxResults,
        gl: 'us',
        hl: 'en'
      }),
    });

    if (!response.ok) {
      throw new Error(`Serper Facebook search failed: ${response.status}`);
    }

    const data = await response.json() as any;
    console.log(`Found ${data.organic?.length || 0} Facebook results`);

    return (data.organic || []).map((item: any, index: number) => ({
      id: `fb_${index}`,
      image_url: item.thumbnail || `https://graph.facebook.com/v12.0/facebook/picture?type=large`,
      post_url: item.link,
      title: item.title || '',
      description: item.snippet || '',
      raw_data: item
    }));

  } catch (error) {
    console.error('Facebook scraping failed:', error);
    return [];
  }
}

// Fallback Instagram search using Serper
async function searchInstagramWithSerper(env: Env, query: string, maxResults: number) {
  try {
    const response = await fetch("https://google.serper.dev/images", {
      method: "POST",
      headers: {
        "X-API-KEY": env.SERPER_API_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        q: `site:instagram.com "${query}" viral popular`,
        num: maxResults,
        safe: "off"
      }),
    });

    if (!response.ok) {
      throw new Error(`Serper Instagram search failed: ${response.status}`);
    }

    const data = await response.json() as any;
    return (data.images || []).map((item: any, index: number) => ({
      id: `ig_serper_${index}`,
      image_url: item.imageUrl,
      post_url: item.link,
      title: item.title || '',
      description: item.snippet || '',
      raw_data: item
    }));

  } catch (error) {
    console.error('Serper Instagram fallback failed:', error);
    return [];
  }
}

// Real engagement analysis using OpenRouter AI
async function analyzeRealEngagement(env: Env, imageData: any, platform: string) {
  try {
    console.log(`Analyzing engagement for ${platform} post: ${imageData.id}`);
    let realMetrics = extractRealMetrics(imageData.raw_data, platform);
    const aiAnalysis = await analyzeWithOpenRouter(env, imageData, platform);
    const engagementScore = calculateEngagementScore(realMetrics, aiAnalysis);

    return {
      image_url: imageData.image_url,
      post_url: imageData.post_url,
      title: imageData.title || aiAnalysis.suggested_title || 'Viral Content',
      description: imageData.description || aiAnalysis.description || '',
      engagement_score: engagementScore,
      views_estimate: realMetrics.views || aiAnalysis.estimated_views || 0,
      likes_estimate: realMetrics.likes || aiAnalysis.estimated_likes || 0,
      comments_estimate: realMetrics.comments || aiAnalysis.estimated_comments || 0,
      shares_estimate: realMetrics.shares || aiAnalysis.estimated_shares || 0,
      author: realMetrics.author || aiAnalysis.author || 'Unknown',
      author_followers: realMetrics.author_followers || aiAnalysis.estimated_followers || 0,
      post_date: realMetrics.post_date || new Date().toISOString(),
      hashtags: realMetrics.hashtags || aiAnalysis.hashtags || []
    };
  } catch (error) {
    console.error('Engagement analysis failed for post:', imageData.id, error);
    const realMetrics = extractRealMetrics(imageData.raw_data, platform);
    return {
      image_url: imageData.image_url,
      post_url: imageData.post_url,
      title: imageData.title || 'Viral Content',
      description: imageData.description || '',
      engagement_score: Math.max(25, realMetrics.likes ? Math.min(realMetrics.likes / 50, 75) : 25),
      views_estimate: realMetrics.views || 1000,
      likes_estimate: realMetrics.likes || 100,
      comments_estimate: realMetrics.comments || 10,
      shares_estimate: realMetrics.shares || 5,
      author: realMetrics.author || 'Unknown',
      author_followers: realMetrics.author_followers || 1000,
      post_date: realMetrics.post_date || new Date().toISOString(),
      hashtags: realMetrics.hashtags || []
    };
  }
}

// Extract real metrics from scraped data
function extractRealMetrics(rawData: any, platform: string) {
  const metrics = {
    views: 0,
    likes: 0,
    comments: 0,
    shares: 0,
    author: '',
    author_followers: 0,
    post_date: new Date().toISOString(),
    hashtags: [] as string[]
  };

  if (!rawData) return metrics;

  try {
    if (platform === 'instagram') {
      metrics.likes = rawData.likesCount || rawData.likes || 0;
      metrics.comments = rawData.commentsCount || rawData.comments || 0;
      metrics.views = rawData.videoViewCount || rawData.viewsCount || 0;
      metrics.author = rawData.ownerUsername || rawData.username || '';
      metrics.author_followers = rawData.ownerFollowersCount || 0;

      if (rawData.hashtags && Array.isArray(rawData.hashtags)) {
        metrics.hashtags = rawData.hashtags;
      }

      if (rawData.takenAtTimestamp || rawData.timestamp) {
        const timestamp = rawData.takenAtTimestamp || rawData.timestamp;
        try {
          let dateObj: Date;
          if (typeof timestamp === 'string') {
            dateObj = new Date(timestamp);
          } else if (typeof timestamp === 'number') {
            if (timestamp > 10000000000) {
              dateObj = new Date(timestamp);
            } else {
              dateObj = new Date(timestamp * 1000);
            }
          } else {
            dateObj = new Date();
          }

          if (isNaN(dateObj.getTime()) || dateObj.getFullYear() < 2000 || dateObj.getFullYear() > 2030) {
            console.warn('Invalid or unreasonable timestamp:', timestamp, 'using current time');
            metrics.post_date = new Date().toISOString();
          } else {
            metrics.post_date = dateObj.toISOString();
          }
        } catch (error) {
          console.error('Error parsing timestamp:', timestamp, error);
          metrics.post_date = new Date().toISOString();
        }
      }
    }

    if (rawData.caption) {
      const hashtagMatches = rawData.caption.match(/#[\w\u00c0-\u024f\u1e00-\u1eff]+/gi);
      if (hashtagMatches) {
        const newHashtags = hashtagMatches.map((tag: string) => tag.substring(1));
        metrics.hashtags = Array.from(new Set([...metrics.hashtags, ...newHashtags]));
      }
    }

  } catch (error) {
    console.error('Error extracting real metrics:', error);
    metrics.post_date = new Date().toISOString();
  }

  return metrics;
}

// AI-powered content analysis using OpenRouter
async function analyzeWithOpenRouter(env: Env, imageData: any, platform: string) {
  try {
    if (!env.OPENROUTER_API_KEY) {
      throw new Error('OpenRouter API key not configured');
    }

    const prompt = `Analyze this ${platform} post for viral potential:

Title: ${imageData.title}
Description: ${imageData.description}
Post URL: ${imageData.post_url}

Please provide a JSON response with:
- estimated_likes: number
- estimated_comments: number
- estimated_shares: number
- estimated_views: number
- estimated_followers: number
- engagement_score: number (0-100)
- viral_factors: array of strings
- suggested_title: string
- description: string
- author: string
- hashtags: array of relevant hashtags
- content_quality: number (0-100)`;

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://viralv1.com",
        "X-Title": "ViralV1 Content Analysis"
      },
      body: JSON.stringify({
        model: "qwen/qwen-2.5-72b-instruct",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 1000,
        temperature: 0.3
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OpenRouter API failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json() as any;
    const content = data.choices[0].message.content;
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }
    throw new Error('No JSON found in analysis response');

  } catch (error) {
    console.error(`OpenRouter analysis failed:`, error);
    return {
      estimated_likes: 100, estimated_comments: 10, estimated_shares: 5,
      estimated_views: 1000, estimated_followers: 1000, engagement_score: 50,
      viral_factors: ['analysis unavailable'], suggested_title: imageData.title,
      description: imageData.description, author: 'unknown', hashtags: [], content_quality: 50
    };
  }
}

function calculateEngagementScore(realMetrics: any, aiAnalysis: any): number {
    let score = 0;
    if (realMetrics.likes > 0) score += Math.min(realMetrics.likes / 100, 30);
    if (realMetrics.comments > 0) score += Math.min(realMetrics.comments / 10, 20);
    if (realMetrics.views > 0) score += Math.min(realMetrics.views / 1000, 25);
    if (aiAnalysis.engagement_score) score += aiAnalysis.engagement_score * 0.25;
    if (aiAnalysis.content_quality > 70) score += 10;
    if (realMetrics.hashtags.length > 3) score += 5;
    return Math.min(Math.round(score), 100);
}

function calculateRealSummary(images: any[]) {
  if (!images.length) {
    return { total_images: 0, avg_engagement: 0, platform_distribution: {}, top_authors: [] };
  }

  const totalEngagement = images.reduce((sum, img) => sum + (img.engagement_score || 0), 0);
  const avgEngagement = totalEngagement / images.length;

  const platformDist: { [key: string]: number } = {};
  const authorStats: { [key: string]: { followers: number; count: number } } = {};

  images.forEach(img => {
    platformDist[img.platform] = (platformDist[img.platform] || 0) + 1;
    if (img.author && img.author !== 'unknown_creator') {
      if (!authorStats[img.author]) {
        authorStats[img.author] = { followers: img.author_followers || 0, count: 0 };
      }
      authorStats[img.author].count++;
    }
  });

  const topAuthors = Object.entries(authorStats)
    .map(([author, stats]) => ({
      author,
      followers: stats.followers,
      posts_count: stats.count
    }))
    .sort((a, b) => b.followers - a.followers)
    .slice(0, 5);

  return {
    total_images: images.length,
    avg_engagement: parseFloat(avgEngagement.toFixed(2)),
    platform_distribution: platformDist,
    top_authors: topAuthors
  };
}

export default app;

// This allows the server to be run directly for local testing
if (process.env.NODE_ENV !== 'production') {
    const port = 8787;
    console.log(`Server is running on port ${port}`);
    serve({
        fetch: app.fetch,
        port: port
    });
}
