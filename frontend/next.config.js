/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www-europe.nissan-cdn.net',
        pathname: '/**',
      },
    ],
  },
};

module.exports = nextConfig;
