import connectMongoDB from '@/lib/mongodb';
import Image from '@/models/Image';

interface ImageData {
    image_name: string;
    s3_url: string;
}

// 이미지 이름으로 DB에서 찾는 함수
export const findImageByName = async (imageName: string) => {
    try {
        // MongoDB 연결
        await connectMongoDB();

        // 이미지 이름으로 검색
        const image = await Image.findOne({ image_name: imageName });

        return image; // 이미지가 존재하면 해당 이미지 반환
    } catch (error) {
        console.error('이미지 검색 중 오류:', error);
        throw error;
    }
};

// MongoDB에 이미지 저장
export const saveImageToDB = async (imageData: ImageData) => {
    try {
        // MongoDB 연결
        await connectMongoDB();

        // 이미지 이름으로 이미 존재하는지 확인
        const existingImage = await findImageByName(imageData.image_name);

        // 이미지가 이미 DB에 존재하면 기존 이미지 반환
        if (existingImage) {
            console.log('이미지가 이미 존재합니다.');
            return existingImage;
        }

        // 이미지 정보 저장 (새로운 이미지)
        const newImage = new Image(imageData);
        const savedImage = await newImage.save();

        return savedImage; // 저장된 이미지 정보 반환
    } catch (error) {
        console.error('이미지 저장 중 오류:', error);
        throw error;
    }
};