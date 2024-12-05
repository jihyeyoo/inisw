import { NextRequest, NextResponse } from 'next/server';
import { uploadFileToS3 } from '@/lib/s3Upload';
import { saveImageToDB } from '@/lib/saveImageToDB';

export async function POST(request: NextRequest) {
    try {
        // FormData로 파일 받기
        const data = await request.formData();
        const file = data.get('file') as File;

        if (!file) {
            return NextResponse.json({ error: '파일이 없습니다.' }, { status: 400 });
        }

        // 파일을 바이트 배열로 변환
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        // S3에 업로드
        const s3Url = await uploadFileToS3({
            buffer,
            originalname: file.name,
            mimetype: file.type,
        });

        // DB에 저장
        const savedImage = await saveImageToDB({
            image_name: file.name,
            s3_url: s3Url,
        });

        // 성공 응답 반환
        return NextResponse.json(
            {
                message: '이미지 업로드 및 저장 성공',
                image: savedImage,
            },
            { status: 200 }
        );
    } catch (error) {
        console.error('Upload error:', error);
        return NextResponse.json(
            {
                error: '이미지 업로드 또는 저장 중 오류 발생',
                details: error instanceof Error ? error.message : error,
            },
            { status: 500 }
        );
    }
}
