import { MetadataRoute } from 'next';
import { SITE_CONFIG } from '@/utils/metadata';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: [
        '/api/',
        '/admin/',
        '/_next/',
        '/private/',
      ],
    },
    sitemap: `${SITE_CONFIG.url}/sitemap.xml`,
  };
}