/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  eslint: {
    // ESLint runs separately in CI; skip during `next build` to avoid
    // circular-reference issues with Next.js 15 flat config migration.
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
