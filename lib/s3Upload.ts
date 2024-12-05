import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { v4 as uuidv4 } from 'uuid';

const s3Client = new S3Client({
    region: process.env.AWS_S3_REGION,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    },
});

interface UploadFile {
    buffer: Buffer;
    originalname: string;
    mimetype: string;
}

export const uploadFileToS3 = async (file: UploadFile): Promise<string> => {
    const uniqueFileName = `lumterior/${uuidv4()}-${file.originalname}`;

    const params = {
        Bucket: process.env.AWS_S3_BUCKET_NAME!,
        Key: uniqueFileName,
        Body: file.buffer,
        ContentType: file.mimetype,
    };

    try {
        const command = new PutObjectCommand(params);
        await s3Client.send(command);

        return `https://${process.env.AWS_S3_BUCKET_NAME}.s3.${process.env.AWS_S3_REGION}.amazonaws.com/${uniqueFileName}`;
    } catch (error) {
        console.error('S3 업로드 오류:', error);
        throw error;
    }
};
