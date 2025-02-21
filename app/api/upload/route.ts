import { NextRequest, NextResponse } from 'next/server';
import { uploadFileToS3 } from '@/lib/s3Upload';
import { saveImageToDB, findImageByName } from '@/lib/saveImageToDB'; // 수정된 경로

export async function POST(request: NextRequest) {
    try {
        // FormData로 파일 받기
        const data = await request.formData();
        const file = data.get('file') as File;

        if (!file) {
            return NextResponse.json({ error: '파일이 없습니다.' }, { status: 400 });
        }

        // 파일 이름 중복 확인 (DB에서 확인)
        const existingImage = await findImageByName(file.name);
        
        if (existingImage) {
            // 이미지가 이미 DB에 존재하면 기존 이미지 반환
            return NextResponse.json(
                {
                    message: '이미 업로드된 파일입니다.',
                    image: existingImage,
                },
                { status: 200 }
            );
        }

        // 파일을 바이트 배열로 변환
        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);

        // S3에 파일 업로드
        const s3Url = await uploadFileToS3({
            buffer,
            originalname: file.name,
            mimetype: file.type,
        });

        // 업로드된 S3 URL을 DB에 저장
        const savedImage = await saveImageToDB({
            image_name: file.name,
            s3_url: s3Url,
        });

        // 성공적으로 저장된 이미지 반환
        return NextResponse.json(
            {
                message: '이미지 업로드 및 저장 성공',
                image: savedImage,
            },
            { status: 200 }
        );

    } catch (error) {
        console.error('Upload error:', error);

        // 에러가 있을 경우 상세 정보 출력
        if (error instanceof Error) {
            console.error('Error Details:', error.message);
        }

        return NextResponse.json(
            {
                error: '이미지 업로드 또는 저장 중 오류 발생',
                details: error instanceof Error ? error.message : 'Unknown error',
            },
            { status: 500 }
        );
    }
}
