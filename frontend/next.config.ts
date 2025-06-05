import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  webpack: (config) => {
    config.resolve.modules.push(__dirname + '/frontend');
    return config;
  },
  images: {
    domains: ['res.cloudinary.com'], // Cloudinaryのホスト名を追加
    remotePatterns: [
      {
        protocol: "https",
        hostname: "res.cloudinary.com",
        port: "",
        pathname: "/my-account/**",
        search: "",
      },
    ],
  },
};

export default nextConfig;
