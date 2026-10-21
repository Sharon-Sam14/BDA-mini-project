/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/regional-trends',
        destination: 'http://127.0.0',
      },
      {
        source: '/api/demand-scores',
        destination: 'http://127.0.0',
      },
    ];
  },
};

export default nextConfig;
