import z from "zod";

export const ViralImageSchema = z.object({
  id: z.number().optional(),
  search_id: z.number().optional(),
  image_url: z.string(),
  post_url: z.string(),
  platform: z.enum(['instagram', 'facebook']),
  title: z.string(),
  description: z.string(),
  engagement_score: z.number(),
  views_estimate: z.number(),
  likes_estimate: z.number(),
  comments_estimate: z.number(),
  shares_estimate: z.number(),
  author: z.string(),
  author_followers: z.number(),
  post_date: z.string(),
  hashtags: z.array(z.string()),
  image_path: z.string().nullable(),
  screenshot_path: z.string().nullable(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export const ViralSearchSchema = z.object({
  id: z.number().optional(),
  query: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  total_results: z.number(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  completed_at: z.string().nullable().optional(),
});

export const SearchRequestSchema = z.object({
  query: z.string().min(1, "Search query is required"),
  max_images: z.number().min(1).max(50).default(20),
  min_engagement: z.number().min(0).default(0),
  platforms: z.array(z.enum(['instagram', 'facebook'])).default(['instagram', 'facebook']),
});

export const SearchResultsSchema = z.object({
  search: ViralSearchSchema,
  images: z.array(ViralImageSchema),
  summary: z.object({
    total_images: z.number(),
    avg_engagement: z.number(),
    platform_distribution: z.record(z.number()),
    top_authors: z.array(z.object({
      author: z.string(),
      followers: z.number(),
      posts_count: z.number(),
    })),
  }),
});

export type ViralImage = z.infer<typeof ViralImageSchema>;
export type ViralSearch = z.infer<typeof ViralSearchSchema>;
export type SearchRequest = z.infer<typeof SearchRequestSchema>;
export type SearchResults = z.infer<typeof SearchResultsSchema>;
