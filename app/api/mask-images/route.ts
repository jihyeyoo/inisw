import { NextApiRequest, NextApiResponse } from 'next';
import { MongoClient } from 'mongodb';
import AWS from 'aws-sdk';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const {
    MONGODB_URI,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_S3_BUCKET_NAME,
    AWS_S3_REGION
  } = process.env;

  AWS.config.update({
    accessKeyId: AWS_ACCESS_KEY_ID,
    secretAccessKey: AWS_SECRET_ACCESS_KEY,
    region: AWS_S3_REGION,
  });

  const s3 = new AWS.S3();
  const client = new MongoClient(MONGODB_URI as string);
  await client.connect();
  const db = client.db('yourDatabaseName'); // 데이터베이스 이름 지정 필요

  try {
    const images = await db.collection('images').find().toArray();

    const imageData = await Promise.all(images.map(async image => {
      const maskImages = image.mask_images.map((mask: any) => ({
        url: mask[`mask_img_${mask.cluster_id.$numberInt}`],
        clusterCenter: {
          x: mask.cluster_center.x.$numberDouble,
          y: mask.cluster_center.y.$numberDouble
        },
        clusterId: mask.cluster_id.$numberInt
      }));

      return {
        ...image,
        s3Url: image.s3_url,
        maskImages
      };
    }));

    res.status(200).json(imageData);
  } catch (error) {
    console.error('Failed to retrieve data', error);
    res.status(500).json({ message: 'Failed to retrieve data' });
  } finally {
    await client.close();
  }
}