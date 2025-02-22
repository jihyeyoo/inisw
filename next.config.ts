import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

module.exports = {
  env: {
    NEXT_PUBLIC_AWS_S3_BUCKET_NAME: process.env.AWS_S3_BUCKET_NAME,
    NEXT_PUBLIC_AWS_S3_REGION: process.env.AWS_S3_REGION,
  },
};

export default nextConfig;
