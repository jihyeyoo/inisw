import connectMongoDB from '@/lib/mongodb';
import Image from '@/models/Image';

interface ImageData {
    image_name: string;
    s3_url: string;
}

// MongoDB에 이미지 저장
export const saveImageToDB = async (imageData: ImageData) => {
    try {
        // MongoDB 연결
        await connectMongoDB();

        // 이미지 정보 저장
        const newImage = new Image(imageData);
        const savedImage = await newImage.save();

        return savedImage; // 저장된 이미지 정보 반환
    } catch (error) {
        console.error('이미지 저장 중 오류:', error);
        throw error;
    }
};
